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
        yield i.get('symbol')


class Pair:
    def __init__(self,name):
        self.name = name
        self.xdata = []
        self.ydata = []
        self.json_data = open(f'{self.name}.json', 'w')

    def json_load(self):
        if len(self.ydata) == 101:
            del self.ydata[0]
            del self.xdata[0]

        with open(f'{self.name}.json', 'w') as file:
            data = dict(zip(self.xdata, self.ydata))
            json.dump(data, file)

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

                time = datetime.datetime.fromtimestamp(int(data.get('time')) // 1000).strftime("%H:%M:%S")
                price = data.get('price')

                if (time not in self.xdata) and (price not in self.ydata):
                    self.xdata.append(time)
                    self.ydata.append(price)

                self.json_load()


def main():
    async def graphs():
        pairs = ["BTC-USDT"]
        pairs = [Pair(name=i) for i in pairs]
        for i in pairs:
            loop.create_task(i.main())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(graphs())
    loop.run_forever()


if __name__ == '__main__':
    main()
