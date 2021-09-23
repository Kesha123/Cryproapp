import threading

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from plotting import GRAPH
from Pairs import get_pairs
from Pairs import Pair, start


class GRAPHlayout(GridLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        CoinList = [i for i in get_pairs()]
        self.main_layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        for btn in CoinList:
            CoinButton = Button(text=f"{btn}", size_hint_y=None, height=40, on_press=lambda btn: self.open_graph(btn))
            self.main_layout.add_widget(CoinButton)

        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll.add_widget(self.main_layout)

    def open_graph(self, coin):

        Coin = Pair(name=coin.text)
        coin_start = threading.Thread(target=start, args=(Coin,))
        coin_start.start()

        grapth = GRAPH(coin=coin.text)
        self.main_layout.clear_widgets()
        self.scroll.clear_widgets()

        self.GraphCoin = GridLayout(rows=1, cols=1)
        self.GraphCoin.add_widget(grapth.layout)
        self.scroll.add_widget(self.GraphCoin)

        update_start = threading.Thread(target=grapth.update_graph)
        update_start.start()

        return self.scroll

    def run(self):
        return self.scroll


class MyApp(App):
    def build(self):
        return GRAPHlayout().run()


if __name__ == '__main__':
    MyApp().run()