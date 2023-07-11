FROM python:3.10
COPY ./ /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright
ENV PYTHONUNBUFFERED=1
RUN apt-get update && \
    apt-get install -y ffmpeg
RUN pip install pipenv &&  \
    pipenv install --deploy --ignore-pipfile --system
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
#RUN PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright pipenv run playwright install --with-deps chromium
RUN pipenv run playwright install
#    pipenv run playwright install-deps
CMD pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app
#RUN pip install waitress
#CMD pipenv run python run_multiprocessing.py

#RUN #curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
#    pip install pipenv \
#    && pipenv install

# ENTRYPOINT pipenv run gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app
# ENTRYPOINT ["/app/run.sh"]

# docker build -t aturret/socialmediacollector .