#web: pipenv run waitress-serve --listen=localhost:$PORT wsgi:app
web: pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT --timeout=0 wsgi:app
#web: pipenv run python ./run.py
#worker: pipenv run python bot_run.py