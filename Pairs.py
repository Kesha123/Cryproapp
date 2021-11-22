import asyncio
import json
import websockets
import requests
import datetime
import certifi
import os
import time as Time


os.environ['SSL_CERT_FILE'] = certifi.where()
connectionID = 12345


def create_user():
    url = requests.post('https://api.kucoin.com/api/v1/bullet-public', verify=False).json()
    token = url.get('data').get('token')
    endpoint = url.get('data').get('instanceServers')[0].get('endpoint')
    socket = "{}?token={}&connectId={}".format(endpoint, token, connectionID)
    ping_interval = url.get('data').get('instanceServers')[0].get('pingInterval')
    ping_timeout = url.get('data').get('instanceServers')[0].get('pingTimeout')
    return socket, ping_interval, ping_timeout


def get_pairs():
    pairs = requests.get("https://api.kucoin.com/api/v1/symbols", verify=False).json().get('data')
    for i in pairs:
        if i.get('symbol').split('-')[1] == "USDT":
            yield i.get('symbol')


class Pair(object):
    def __init__(self, name=''):
        self.name = name
        self.data = []
        self.xdata = []
        self.ydata = []
        self.timer = 0
        self.unsubscribe = False

    async def main(self, websocket=create_user()):
        async with websockets.connect(websocket[0], ping_interval=websocket[1],
                                      ping_timeout=websocket[2]) as connection:

            pingInterval = websocket[1] // 1000
            pingTimeout = websocket[2] // 1000

            data = json.dumps({
                "id": f"{connectionID}",
                "type": "subscribe",
                "topic": f"/market/ticker:{self.name}",
                "privateChannel": "false",
                "response": "true"
            })

            await connection.send(data)
            result = await connection.recv()
            result = await connection.recv()

            while True:
                start_time = Time.time()
                response = json.loads(await connection.recv())
                try:
                    data = response.get('data')

                    time = datetime.datetime.fromtimestamp(int(data.get('time')) // 1000).strftime("%S")
                    full_time = datetime.datetime.fromtimestamp(int(data.get('time')) // 1000).strftime(
                        "%d.%m.%Y %H:%M")
                    price = data.get('price')

                    if (time not in self.xdata) and (price not in self.ydata):
                        coin_data = (float(time), float(price), full_time, self.name,)
                        self.data.append(coin_data)
                        self.xdata.append(time)
                        self.ydata.append(float(price))

                        if float(time) == 59.0:
                            self.xdata.clear()
                            self.ydata.clear()
                            self.data.clear()

                    self.timer += Time.time() - start_time

                    if pingTimeout <= float(self.timer) <= pingInterval:
                        ping = json.dumps(
                            {
                                "id": connectionID,
                                "type": "ping",
                            }
                        )
                        await connection.send(ping)
                        self.timer *= 0

                except Exception as ex:
                    pass

                if self.unsubscribe:
                    unsubscribe = json.dumps(
                        {
                            "id": "1545910840805",
                            "type": "unsubscribe",
                            "topic": f"/market/ticker:{self.name}",
                            "privateChannel": "false",
                            "response": "false"
                        })

                    await connection.send(unsubscribe)
                    break

    def __delete__(self, instance):
        del self
        print("Pair is deleted")


def start(pair):
    async def graphs():
        loop.create_task(pair.main())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(graphs())
    loop.run_forever()


if __name__ == '__main__':
    pass
