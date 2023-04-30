from waitress import serve
import app


def run():
    serve(app.create_app(), host='127.0.0.1', port=app.settings.env_var.get('PORT', '1045'), threads=8,
          url_scheme=app.settings.env_var.get('HTTP_MODE', 'http'))


if __name__ == '__main__':
    run()
