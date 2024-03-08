# import psycogreen.gevent

# # https://github.com/psycopg/psycogreen/blob/39a258cb4040b88b60a7600f6942e651a28db9a7/README.rst#module-psycogreengevent
# psycogreen.gevent.patch_psycopg()

import os

backlog = int(os.getenv("GUNICORN_BACKLOG", "4096"))
workers = int(os.getenv("GUNICORN_WORKERS", "3"))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gevent")
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", "100"))
