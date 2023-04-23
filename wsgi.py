from app import create_app, atelebot, threading
import os

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '1045')))
    telebot_thread = threading.Thread(target=atelebot.bot.polling(), daemon=True)
    telebot_thread.start()