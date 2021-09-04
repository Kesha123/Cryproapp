import asyncio
import websockets

import requests
#from websocket import create_connection
import json
import datetime


def get_pairs():
    pairs = requests.get("https://api.kucoin.com/api/v1/symbols").json().get('data')
    for i in pairs:
        yield i.get('symbol')


def create_user():
    url = requests.post('https://api.kucoin.com/api/v1/bullet-public').json()
    token = url.get('data').get('token')
    endpoint = url.get('data').get('instanceServers')[0].get('endpoint')
    socket = "{}?token={}&connectId=12345".format(endpoint, token)
    return socket


async def main(websocket = create_user()):
    async with websockets.connect(websocket) as connection:
        data = json.dumps({
            "id": "12345",
            "type": "subscribe",
            "topic": f"/market/ticker:BTC-USDT",
            "privateChannel": "false",
            "response": "true"
        })
        result = await connection.recv()
        result = await connection.recv()

        while True:
            data = json.loads(await connection.recv()).get('data')
            yield data.get('price'), datetime.datetime.fromtimestamp(int(data.get('time')) // 1000)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

