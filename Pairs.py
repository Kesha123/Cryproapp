import asyncio
import json
import websockets
import requests
import datetime


def create_user():
    url = requests.post('https://api.kucoin.com/api/v1/bullet-public').json()
    token = url.get('data').get('token')
    endpoint = url.get('data').get('instanceServers')[0].get('endpoint')
    socket = "{}?token={}&connectId=12345".format(endpoint, token)
    return socket


def get_pairs():
    pairs = requests.get("https://api.kucoin.com/api/v1/symbols").json().get('data')
    for i in pairs:
        if i.get('symbol').split('-')[1] == "USDT":
            yield i.get('symbol')


class Pair:
    def __init__(self, name):
        self.name = name
        self.data = []
        self.xdata = []
        self.ydata = []
        self.full_time = ''

    async def main(self, websocket=create_user()):
        async with websockets.connect(websocket, ping_interval=None) as connection:
            data = json.dumps({
                "id": "12345",
                "type": "subscribe",
                "topic": f"/market/ticker:{self.name}",
                "privateChannel": "false",
                "response": "true"
            })

            await connection.send(data)
            result = await connection.recv()
            result = await connection.recv()

            while True:
                data = json.loads(await connection.recv()).get('data')

                time = datetime.datetime.fromtimestamp(int(data.get('time')) // 1000).strftime("%S")
                full_time = datetime.datetime.fromtimestamp(int(data.get('time')) // 1000).strftime("%d.%m.%Y %H:%M")
                price = data.get('price')

                if (time not in self.xdata) and (price not in self.ydata):
                    coin_data = (float(time), float(price), full_time)
                    self.data.append(coin_data)
                    self.xdata.append(time)
                    self.ydata.append(float(price))

                    if float(time) == 59.0:
                        self.data.clear()


def start(pair):
    async def graphs():
        loop.create_task(pair.main())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(graphs())
    loop.run_forever()
