#!/bin/bash
# pipenv run gunicorn -w 4 -b 0.0.0.0:1045 wsgi:app
pipenv run waitress-serve --listen=*:1045 wsgi:app