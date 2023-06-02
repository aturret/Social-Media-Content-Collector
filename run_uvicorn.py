from app import create_app
from uvicorn import run
import asyncio

app = asyncio.run(create_app())

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=1046)

