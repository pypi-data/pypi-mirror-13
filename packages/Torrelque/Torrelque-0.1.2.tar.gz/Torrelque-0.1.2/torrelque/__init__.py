'''Tornado Redis-based reliable working queue.'''


import json
import uuid
import time
import hashlib

from tornado import gen
from tornado.ioloop import PeriodicCallback
import tornadoredis


class Torrelque:
    
    stale_timeout = 120
    '''Default timeout for a task in working queue to be considered stale.'''

    sweep_interval = 30
    '''Default interval between the housekeeping routine.'''
    
    keys = {
        'pending' : 'pending',  # list
        'working' : 'working',  # sorted set
        'delayed' : 'delayed',  # sorted set
        'tasks'   : 'tasks',    # hash
        'stats'   : 'stats'     # prefix for hashes
    }
    '''Redis keys dict which values are prefixed on instance initialisation.'''
    
    _serialiser = None
    '''Task serialiser that converts task object into and from
    string representation.'''
    
    _redis = None
    '''Instance of tornadoredis.Client.'''
    
    _ioloop = None
    '''Tornado IO loop'''
    
    _timer = None
    '''Periodic housekeeping runner.'''
        

    def __init__(self, redis, ioloop, prefix = 'trq', serialiser = json, sweep_interval = None):
        self._redis = redis
        self._ioloop = ioloop
        self._serialiser = serialiser
        
        self.keys = {k: '{}:{}'.format(prefix, v) for k, v in self.keys.items()}
        
        sweep_interval = sweep_interval or self.sweep_interval
        self._timer = PeriodicCallback(self.sweep, sweep_interval * 1000, ioloop)
        
    def _get_stats_key(self, task_id):
        return '{}:{}'.format(self.keys['stats'], task_id)
    
    @gen.coroutine
    def _call_script(self, script, keys, args):
        '''Currently `.tornadoredis` only implements EVAL and EVALSHA from
        Redis scripting functions. So the helper function makes first attempt 
        with EVALSHA resorting to EVAL if needed.'''
        
        digest = hashlib.sha1(script.encode()).hexdigest()
        result = yield gen.Task(self._redis.evalsha, digest, keys = keys, args = args)
        if isinstance(result, tornadoredis.ResponseError):
            if result.message.startswith('NOSCRIPT'):
                result = yield gen.Task(self._redis.eval, script, keys = keys, args = args)
                if isinstance(result, tornadoredis.ResponseError):
                    raise result
            else:
                raise result
        
        return result
    
    @gen.coroutine
    def enqueue(self, task, task_timeout = None):
        '''Enqueue arbitrary (though serialisable) *task* object into 
        working queue. Return UUID to reference the task.'''
        
        task_timeout = task_timeout or self.stale_timeout
        task_id = '{}-{}'.format(uuid.uuid1().hex, task_timeout)
        task_data = self._serialiser.dumps(task)

        pipe = self._redis.pipeline(transactional = True)
        pipe.lpush(self.keys['pending'], task_id)
        pipe.hset(self.keys['tasks'], task_id, task_data)
        pipe.hset(self._get_stats_key(task_id), 'enqueue_time', time.time())
        yield gen.Task(pipe.execute)
                
        return task_id 
    
    @gen.coroutine
    def dequeue(self, timeout = None):
        '''Get a task from working queue.'''
        
        # The trick with BRPOPLPUSH makes it possible to make dequeue()
        # blocking, thus avoid overhead and latency caused by polling.
        # Later on the ``task_id`` LREM will be applied, which is less
        # efficient that LPOP or RPOP, but because the rotation has just
        # occurred the entry being deleted is at the beginning of the 
        # list and LREM complexity is close to O(1).
        task_id = yield gen.Task(self._redis.brpoplpush, self.keys['pending'], 
            self.keys['pending'], timeout = timeout or 0)
        if not task_id:
            return None, None
        
        script = '''
            local pending, working, tasks = unpack(KEYS) 
            local task_id = ARGV[1]
            local now = ARGV[2]
            
            local removed = redis.call('LREM', pending, 1, task_id)
            if removed == 0 then
                return {0, 'null'}
            end
            
            local task_data = redis.call('HGET', tasks, task_id)
            
            local stale = now + task_id:match('-([^\-]+)$')
            redis.call('ZADD', working, stale, task_id)
            
            local stats = KEYS[4] .. ':' .. task_id
            redis.call('HSET', stats, 'last_dequeue_time', now)
            redis.call('HINCRBY', stats, 'dequeue_count', 1)
            
            return {task_id, task_data}
        '''
        
        keys = [self.keys[k] for k in ('pending', 'working', 'tasks', 'stats')]
        args = [task_id, time.time()]
        task_id, task_data = yield self._call_script(script, keys, args)
        
        return task_id or None, self._serialiser.loads(task_data)

    @gen.coroutine
    def requeue(self, task_id, delay = None):
        '''Return failed task into into working queue. Its dequeue may be 
        deferred on given amount of seconds and then the task is put in 
        delayed queue.'''
        
        now = time.time()
        pipe = self._redis.pipeline(transactional = True)
        pipe.zrem(self.keys['working'], task_id)
        
        if delay is None:
            pipe.lpush(self.keys['pending'], task_id)
            
            stats_key = self._get_stats_key(task_id)
            pipe.hset(stats_key, 'last_requeue_time', now)
            pipe.hincrby(stats_key, 'requeue_count', 1)
        else:
            pipe.zadd(self.keys['delayed'], now + delay, task_id)
        
        yield gen.Task(pipe.execute)
    
    @gen.coroutine
    def release(self, task_id):
        '''Mark task as successfully processed.'''
        
        pipe = self._redis.pipeline(transactional = True)
        pipe.zrem(self.keys['working'], task_id)
        pipe.hdel(self.keys['tasks'], task_id)
        pipe.delete(self._get_stats_key(task_id))
        yield gen.Task(pipe.execute)

    @gen.coroutine
    def sweep(self):
        '''Return stale tasks from working queue into pending list. Move ready
        deferred tasks into pending list.'''
        
        script = '''
            local function requeue(pending_key, target_key, stats_prefix, now)
                local task_ids = redis.call('ZRANGEBYSCORE', target_key, 0, now)
                if #task_ids == 0 then
                    return 0
                end
                
                redis.call('LPUSH', pending_key, unpack(task_ids))
                redis.call('ZREM', target_key, unpack(task_ids))
                
                local stats_key
                for _, task_id in ipairs(task_ids) do
                    stats_key = stats_prefix .. ':' .. task_id
                    redis.call('HSET', stats_key, 'last_requeue_time', now)
                    redis.call('HINCRBY', stats_key, 'requeue_count', 1)
                end
                
                return #task_ids
            end
        
            local pending, working, delayed, stats = unpack(KEYS)
            local now = ARGV[1]
            
            return requeue(pending, working, stats, now) + 
                requeue(pending, delayed, stats, now)
        '''
        
        keys = [self.keys[k] for k in ('pending', 'working', 'delayed', 'stats')]
        result = yield self._call_script(script, keys, args = [time.time()])
        
        return result

    def schedule_sweep(self):
        self._timer.start()
    
    def unschedule_sweep(self):
        self._timer.stop()

    @gen.coroutine
    def get_stats(self):
        pipe = self._redis.pipeline()
        pipe.hlen(self.keys['tasks'])
        pipe.llen(self.keys['pending'])
        pipe.zcard(self.keys['working'])
        pipe.zcard(self.keys['delayed'])
        result = yield gen.Task(pipe.execute)
        
        return dict(zip(('tasks', 'pending', 'working', 'delayed'), result))
    
    @gen.coroutine
    def get_task_stats(self, task_id):
        '''Return dictionary with task's counters.'''
        
        result = yield gen.Task(self._redis.hgetall, self._get_stats_key(task_id))
        if not result:
            return None
        
        return {
            'enqueue_time'       : float(result['enqueue_time']),
            'last_dequeue_time'  : float(result.get('last_dequeue_time', 0)) or None,
            'dequeue_count'      : int(result.get('dequeue_count', 0)),
            'last_requeue_time'  : float(result.get('last_requeue_time', 0)) or None,
            'requeue_count'      : int(result.get('requeue_count', 0))
        }

