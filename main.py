import asyncio
import random

import websockets
import requests
import json
import datetime
import matplotlib.pyplot as plt


fig = plt.figure()
ax = fig.add_subplot(111)
fig.show()

xdata = []
ydata = []
last_price = '0'


def get_pairs():
    pairs = requests.get("https://api.kucoin.com/api/v1/symbols").json().get('data')
    for i in pairs:
        yield i.get('symbol')


pair = random.sample(list(get_pairs()), 1)[0]
coin_usd = f"{pair.split('-')[0]}-USDT"


def update_graph():
    ax.plot(xdata, ydata, color='g')
    ax.legend([f"Last price: {ydata[-1]}$", pair])

    fig.canvas.draw()
    plt.pause(0.00001)


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
            "topic": f"/market/ticker:{pair}",
            "privateChannel": "false",
            "response": "true"
        })

        await connection.send(data)
        result = await connection.recv()
        result = await connection.recv()

        while True:
            data = json.loads(await connection.recv()).get('data')

            time = datetime.datetime.fromtimestamp(int(data.get('time')) // 1000)
            price = data.get('price')
            xdata.append(time)
            ydata.append(price)

            update_graph()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

