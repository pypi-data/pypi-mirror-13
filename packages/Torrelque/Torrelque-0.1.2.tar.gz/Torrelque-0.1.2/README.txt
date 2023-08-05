*********
Torrelque
*********

Torrelque is a Python3 package that provides a reliable Redis-backed queues and runs on
Tornado IO-loop.  

Without further ado it's easy to say the package is an implementation of the queue described
in `this blog post <http://blog.bronto.com/engineering/reliable-queueing-in-redis-part-1/>`_ 
with some required changes and improvements.  

There's also a related, synchronous queue package called `saferedisqueue 
<https://pypi.python.org/pypi/saferedisqueue>`_. 

Install
=======
.. sourcecode:: bash

    pip install Torrelque
    
Use
===
.. sourcecode:: python

    #!/usr/bin/env python3
    
    
    import random
    import logging
    
    import tornadoredis
    from tornado import gen, ioloop
    from torrelque import Torrelque
    
    
    logger = logging.getLogger(__name__)
    
    
    @gen.coroutine
    def produce():
        redis = tornadoredis.Client()
        queue = Torrelque(redis, ioloop.IOLoop.current())
        while True:
            for _ in range(5):
                task = {'value': random.randint(0, 99)}
                logger.debug('Produced task %s', task)
                yield queue.enqueue(task)
            yield gen.sleep(10)
    
    
    @gen.coroutine
    def process(task_data):
        logger.debug('Consmed task %s', task_data)
        yield gen.sleep(1)
    
    @gen.coroutine
    def consume():
        redis = tornadoredis.Client()
        queue = Torrelque(redis, ioloop.IOLoop.current())
        while True:
            task_id, task_data = yield queue.dequeue()
            if not task_id:
                continue
            try:
                yield process(task_data)
                yield queue.release(task_id)
            except Exception:
                logger.exception('Job processing has failed')
                queue.requeue(task_id, delay = 30)
    
    @gen.coroutine
    def main():
        for _ in range(4):
            ioloop.IOLoop.current().spawn_callback(consume)
        
        yield produce()
    
    
    if __name__ == '__main__':
        logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s %(message)s')
        ioloop.IOLoop.instance().run_sync(lambda: main())
    
