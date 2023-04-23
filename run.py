from waitress import serve
import app

if __name__ == '__main__':
    bot_process = app.bot_start.start_bot_process()  # Start the Telegram bot process
    monitor_thread = app.threading.Thread(target=app.bot_start.monitor_bot_process, args=(bot_process,))
    monitor_thread.start()
    # Run the Flask app with Waitress
    serve(app.create_app(), host='127.0.0.1', port=app.settings.env_var.get('PORT', '1045'))