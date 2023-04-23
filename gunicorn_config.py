bind = "127.0.0.1:1045"  # Bind the server to the desired address and port
workers = 1  # Use 1 worker processes
threads = 4  # Use 4 threads per worker process
worker_class = "sync"  # Choose the worker class, e.g. 'sync', 'gevent', 'eventlet', etc.
module_name = "your_flask_app"  # Replace this with the name of your Flask app module
callable_name = "app"