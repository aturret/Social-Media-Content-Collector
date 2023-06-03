#!/bin/bash
pipenv run gunicorn -w 1 -b 0.0.0.0:1046 wsgi:app
#pipenv run waitress-serve --listen=*:1045 --threads=5 wsgi:app
#web: pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 600 --threads 1 --log-level=debug wsgi:app
#web: pipenv run waitress-serve --listen=*:$PORT wsgi:app
#worker: pipenv run python ./bot_run.py
#web: pipenv run python ./run_multiprocessing.py