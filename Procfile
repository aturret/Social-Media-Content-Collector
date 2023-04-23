#web: pipenv run waitress-serve --listen=*:$PORT --threads=5 wsgi:app
#worker: pipenv run python bot_run.py
web: pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 600 wsgi:app
#web: pipenv run python ./run.py