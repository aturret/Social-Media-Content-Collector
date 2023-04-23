from app import atelebot
import time

if __name__ == '__main__':
    # atelebot.bot.polling()
    while True:
        try:
            # atelebot.bot.polling(none_stop=True, timeout=90)
            atelebot.bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            time.sleep(5)
            continue
    # app.bot_start.start_bot_thread()
    # bot_process = app.bot_start.start_bot_process()  # Start the Telegram bot process
    # monitor_thread = app.threading.Thread(target=app.bot_start.monitor_bot_process, args=(bot_process,))
    # monitor_thread.start()

