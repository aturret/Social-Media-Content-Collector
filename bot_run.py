import app

bot_process = app.bot_start.start_bot_process()  # Start the Telegram bot process
monitor_thread = app.threading.Thread(target=app.bot_start.monitor_bot_process, args=(bot_process,))
monitor_thread.start()

