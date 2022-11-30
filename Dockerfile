FROM python:3.10
COPY ./ /app
WORKDIR /app
# EXPOSE 1045
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
    && python get-pip.py \
#    && pip install pyTelegramBotAPI \
#    && pip install python-telegram-bot \
    && pip install pipenv \
    && pipenv install
    # && pipenv run gunicorn -w 4 -b 0.0.0.0:1045 wsgi:app
# CMD 
ENTRYPOINT pipenv run gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
# ENTRYPOINT ["/app/run.sh"]