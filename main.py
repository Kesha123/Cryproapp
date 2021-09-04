import asyncio

import requests
from websocket import create_connection
import json
import datetime


async def get_pairs():
    pairs = requests.get("https://api.kucoin.com/api/v1/symbols").json().get('data')
    for i in pairs:
        yield i.get('symbol')


async def main():
    url = requests.post('https://api.kucoin.com/api/v1/bullet-public').json()
    token = url.get('data').get('token')
    endpoint = url.get('data').get('instanceServers')[0].get('endpoint')
    socket = "{}?token={}&connectId=12345".format(endpoint, token)

    currencies = [i for i in get_pairs()]

    data = json.dumps({
        "id": "12345",
        "type": "subscribe",
        "topic": f"/market/ticker:BTC-USDT",
        "privateChannel": "false",
        "response": "true"
    })

    connection = create_connection(socket)

    connection.send(data)
    result = connection.recv()
    result = connection.recv()

    while True:
        data = json.loads(connection.recv()).get('data')
        yield data.get('price'), datetime.datetime.fromtimestamp(int(data.get('time'))//1000)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()