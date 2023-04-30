import app.settings as settings
import run_webhook
import run_multiprocessing


def main():
    if settings.env_var.get('RUN_MODE', 'webhook') == 'webhook':
        run_webhook.run()
    elif settings.env_var.get('RUN_MODE', 'webhook') == 'multiprocessing':
        run_multiprocessing.run()


if __name__ == '__main__':
    main()
