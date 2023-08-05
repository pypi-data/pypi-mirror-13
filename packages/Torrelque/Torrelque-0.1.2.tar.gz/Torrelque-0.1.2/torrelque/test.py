'''Unit tests for Torrelque.'''


import time

import tornadoredis
import tornado.testing
from tornado import gen

from . import Torrelque


class TestTorrelque(tornado.testing.AsyncTestCase):
    
    redis = None
    '''Redis client'''
    

    def setUp(self):
        super().setUp()
        
        self.redis = tornadoredis.Client(selected_db = 1) 
        self.testee = Torrelque(self.redis, self.io_loop)
        
        self.io_loop.run_sync(lambda: gen.Task(self.redis.flushdb))
        
    @gen.coroutine
    def _get_state(self):
        pending = yield gen.Task(self.redis.lrange, self.testee.keys['pending'], 0, -1)
        working = yield gen.Task(self.redis.zrange, self.testee.keys['working'], 0, -1, True)
        delayed = yield gen.Task(self.redis.zrange, self.testee.keys['delayed'], 0, -1, True)
        tasks = yield gen.Task(self.redis.hgetall, self.testee.keys['tasks'])
        return pending, working, delayed, tasks
        
    @tornado.testing.gen_test
    def test_enqueue(self):
        now = time.time()
        
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 5)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        uuid, timeout = task_id1.split('-')
        self.assertEqual(32, len(uuid))
        self.assertEqual('5', timeout)

        uuid, timeout = task_id2.split('-')
        self.assertEqual(32, len(uuid))
        self.assertEqual('120', timeout)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)
        
        actual = yield self.testee.get_task_stats(task_id1)
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
        self.assertEqual({
            'last_requeue_time': None, 
            'last_dequeue_time': None, 
            'requeue_count': 0, 
            'dequeue_count': 0
        }, actual)
        
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([task_id2, task_id1], pending)
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)
    
    @tornado.testing.gen_test
    def test_dequeue(self):
        now = time.time()
        
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 5)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        task_id, task_data = yield self.testee.dequeue()
        self.assertEqual(task_id1, task_id)
        self.assertEqual({'foo': 123}, task_data)

        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 1, 'pending': 1, 'delayed': 0, 'tasks': 2}, actual)

        actual = yield self.testee.get_task_stats(task_id1)
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta = 0.2)
        self.assertEqual({
            'last_requeue_time': None, 
            'requeue_count': 0, 
            'dequeue_count': 1
        }, actual)
        
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([task_id2], pending)
        
        self.assertEqual(1, len(working))
        self.assertEqual(task_id1, working[0][0])
        self.assertAlmostEqual(now + 5, working[0][1], delta = 0.2)
        
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)


        task_id, task_data = yield self.testee.dequeue()
        self.assertEqual(task_id2, task_id)
        self.assertEqual({'bar': [1, 2, 3]}, task_data)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 2, 'pending': 0, 'delayed': 0, 'tasks': 2}, actual)
        
        actual = yield self.testee.get_task_stats(task_id1)
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta = 0.2)
        self.assertEqual({
            'last_requeue_time': None, 
            'requeue_count': 0, 
            'dequeue_count': 1
        }, actual)
        
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([], pending)
        
        self.assertEqual(2, len(working))
        self.assertEqual(task_id1, working[0][0])
        self.assertAlmostEqual(now + 5, working[0][1], delta = 0.2)
        self.assertEqual(task_id2, working[1][0])
        self.assertAlmostEqual(now + 120, working[1][1], delta = 0.2)
        
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)
        
        
        task_id, task_data = yield self.testee.dequeue(timeout = 1)
        self.assertIsNone(task_id)
        self.assertIsNone(task_data)

    @tornado.testing.gen_test
    def test_dequeue_concurrent(self):
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 5)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        actual = []
        
        @gen.coroutine
        def create_consumer():
            redis = tornadoredis.Client(selected_db = 1) 
            queue = Torrelque(redis, self.io_loop)
            while True:
                task_id, _ = yield queue.dequeue()
                yield queue.release(task_id)
                if task_id is None:
                    break
                actual.append(task_id)
                
        @gen.coroutine
        def run_consumers():
            yield [create_consumer() for _ in range(8)]

        self.io_loop.add_callback(run_consumers)
        
        while True:
            size = yield gen.Task(self.redis.hlen, self.testee.keys['tasks'])
            if not size:
                break
            yield gen.sleep(0.1)
            
        self.assertEqual([task_id1, task_id2], actual)

    @tornado.testing.gen_test
    def test_requeue(self):
        now = time.time()
        
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 5)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        task_id, _ = yield self.testee.dequeue()
        yield self.testee.requeue(task_id, delay = None)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)
        
        actual = yield self.testee.get_task_stats(task_id1)
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta = 0.2)
        self.assertAlmostEqual(now, actual.pop('last_requeue_time'), delta = 0.2)
        self.assertEqual({
            'requeue_count': 1, 
            'dequeue_count': 1
        }, actual)
        
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([task_id1, task_id2], pending)
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)
        
    @tornado.testing.gen_test
    def test_requeue_delayed(self):
        now = time.time()
        
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 5)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        task_id, _ = yield self.testee.dequeue()
        yield self.testee.requeue(task_id, delay = 3600)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 0, 'pending': 1, 'delayed': 1, 'tasks': 2}, actual)
        
        actual = yield self.testee.get_task_stats(task_id1)
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta = 0.2)
        self.assertEqual({
            'last_requeue_time' : None,
            'requeue_count': 0, 
            'dequeue_count': 1
        }, actual)
        
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([task_id2], pending)
        
        self.assertEqual([], working)
        
        self.assertEqual(1, len(delayed))
        self.assertEqual(task_id1, delayed[0][0])
        self.assertAlmostEqual(now + 3600, delayed[0][1], delta = 0.2)

        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)

    @tornado.testing.gen_test
    def test_release(self):
        yield self.testee.enqueue({'foo': 123}, task_timeout = 5)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        task_id, _ = yield self.testee.dequeue()
        yield self.testee.release(task_id)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 0, 'pending': 1, 'delayed': 0, 'tasks': 1}, actual)
        
        actual = yield self.testee.get_task_stats(task_id)
        self.assertIsNone(actual)
        
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([task_id2], pending)
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({task_id2: '{"bar": [1, 2, 3]}'}, tasks)
    
    @tornado.testing.gen_test
    def test_sweep(self):
        actual = yield self.testee.sweep()
        self.assertEqual(0, actual)
        
        now = time.time()
        
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 0.1)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        yield [self.testee.dequeue(), self.testee.dequeue()]
        yield self.testee.requeue(task_id2, delay = 0.25)
        
        actual = yield self.testee.sweep()
        self.assertEqual(0, actual)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 1, 'pending': 0, 'delayed': 1, 'tasks': 2}, actual)
        
        for id in (task_id1, task_id2):
            actual = yield self.testee.get_task_stats(id)
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta = 0.1)
            self.assertEqual({
                'last_requeue_time': None, 
                'requeue_count': 0, 
                'dequeue_count': 1
            }, actual)
            
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([], pending)
        
        self.assertEqual(1, len(working))
        self.assertEqual(task_id1, working[0][0])
        self.assertAlmostEqual(now + 0.1, working[0][1], delta = 0.1)

        self.assertEqual(1, len(delayed))
        self.assertEqual(task_id2, delayed[0][0])
        self.assertAlmostEqual(now + 0.25, delayed[0][1], delta = 0.1)
        
        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)
        
        yield gen.sleep(0.25)
        
        requeue_time = time.time()
        actual = yield self.testee.sweep()
        self.assertEqual(2, actual)
        
        actual = yield self.testee.get_stats()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)
        
        for id in (task_id1, task_id2):
            actual = yield self.testee.get_task_stats(id)
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta = 0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta = 0.1)
            self.assertAlmostEqual(requeue_time, actual.pop('last_requeue_time'), delta = 0.1)
            self.assertEqual({
                'requeue_count': 1, 
                'dequeue_count': 1
            }, actual)
            
        pending, working, delayed, tasks = yield self._get_state()
        self.assertEqual([task_id2, task_id1], pending)
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1: '{"foo": 123}', 
            task_id2: '{"bar": [1, 2, 3]}'
        }, tasks)

    @tornado.testing.gen_test
    def test_sweep_schedule(self):
        self.testee = Torrelque(self.redis, self.io_loop, sweep_interval = 0.2)

        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 0.1)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        yield [self.testee.dequeue(), self.testee.dequeue()]
        yield self.testee.requeue(task_id2, delay = 0.15)
        
        self.testee.schedule_sweep()
        
        pending, _, _, _ = yield self._get_state()
        self.assertEqual([], pending)
        
        yield gen.sleep(0.2)
        
        pending, _, _, _ = yield self._get_state()
        self.assertEqual([task_id2, task_id1], pending)
        
        
        yield [self.testee.dequeue(), self.testee.dequeue()]
        yield [self.testee.release(task_id1), self.testee.release(task_id2)]
        
        task_id1 = yield self.testee.enqueue({'foo': 123}, task_timeout = 0.1)
        task_id2 = yield self.testee.enqueue({'bar': [1, 2, 3]})
        
        yield [self.testee.dequeue(), self.testee.dequeue()]
        yield self.testee.requeue(task_id2, delay = 0.15)
        
        self.testee.unschedule_sweep()
    
        pending, _, _, _ = yield self._get_state()
        self.assertEqual([], pending)
        
        yield gen.sleep(0.2)

        pending, _, _, _ = yield self._get_state()
        self.assertEqual([], pending)

