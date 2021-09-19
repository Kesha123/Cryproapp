from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from plotting import GRAPH
from Pairs import get_pairs
import asyncio


class GRAPHlayout(GridLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.coins = [GRAPH(coin=coin) for coin in get_pairs()]
        self.coins = [GRAPH(coin="ETH-USDT"), GRAPH(coin="BTC-USDT"),]
        layout = GridLayout(cols=1)

        for i in self.coins:
            layout.add_widget(i)

        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(layout)

    def run(self):
        async def tasks():
            for coin in self.coins:
                loop.create_task(coin.update_graph())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks())
        loop.run_forever()


class MyApp(App):
    def build(self):
        return GRAPHlayout()


if __name__ == '__main__':
    MyApp().run()