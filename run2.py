from waitress import serve
from concurrent.futures import ThreadPoolExecutor
import app


def main():
    website = app.create_app()
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(serve, website, host='0.0.0.0', port=app.settings.env_var.get('PORT', '1045'), threads=4,
                        url_scheme=app.settings.env_var.get('HTTP_MODE', 'http'))
        executor.submit(app.atelebot.bot.polling(non_stop=True, timeout=app.telebot_timeout))


if __name__ == '__main__':
    main()