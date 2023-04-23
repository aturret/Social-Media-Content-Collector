from . import atelebot
import threading, multiprocessing, logging
import time

def bot_polling():
    while True:
        try:
            atelebot.bot.polling(none_stop=False)
        except Exception as e:
            logging.error(f"An exception occurred in the bot process: {e}")
            time.sleep(10)  # Sleep for a while before retrying
        else:
            break  # Exit the loop if bot.polling() returns without an exception


def start_bot_process():
    bot_process = multiprocessing.Process(target=bot_polling)
    bot_process.start()
    return bot_process


def monitor_bot_process(bot_process):
    while True:
        time.sleep(30)  # Check the bot process status every 30 seconds
        if not bot_process.is_alive():
            logging.warning("Bot process has stopped, restarting...")
            bot_process.terminate()
            bot_process.join()
            bot_process = start_bot_process()
