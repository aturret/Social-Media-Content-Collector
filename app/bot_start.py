from . import atelebot
import multiprocessing, logging, threading
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


def start_bot_thread():
    bot_thread = threading.Thread(target=bot_polling)
    bot_thread.start()
    return bot_thread


def monitor_bot_thread(bot_thread):
    while True:
        time.sleep(30)  # Check the bot thread status every 30 seconds
        if not bot_thread.is_alive():
            logging.warning("Bot thread has stopped, restarting...")
            bot_thread = start_bot_thread()


def monitor_bot_process(bot_process):
    while True:
        time.sleep(30)  # Check the bot process status every 30 seconds
        if not bot_process.is_alive():
            logging.warning("Bot process has stopped, restarting...")
            bot_process.terminate()
            bot_process.join()
            bot_process = start_bot_process()
