from gevent import monkey
import multiprocessing

monkey.patch_all()

workers = 4
worker_class = "gevent"
