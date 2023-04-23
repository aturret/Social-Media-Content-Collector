FROM python:3.9.16
COPY ./ /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile --system
RUN pip install waitress
CMD pipenv run python run.py
#RUN #curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
#    pip install pipenv \
#    && pipenv install

# ENTRYPOINT pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app
# ENTRYPOINT ["/app/run.sh"]

# docker build -t aturret/socialmediacollector .