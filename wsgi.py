from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '1045'))