FROM python:3.10
COPY ./ /app
WORKDIR /app
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install pipenv &&  \
    pipenv install --deploy --ignore-pipfile --system && \
    pipenv run playwright install
CMD pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app
#RUN pip install waitress
#CMD pipenv run python run_multiprocessing.py

#RUN #curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
#    pip install pipenv \
#    && pipenv install

# ENTRYPOINT pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app
# ENTRYPOINT ["/app/run.sh"]

# docker build -t aturret/socialmediacollector .