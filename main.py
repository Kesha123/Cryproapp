import threading

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from plotting import GRAPH
from Pairs import Pair, start, get_pairs


class StopableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StopableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class GRAPHlayout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        CoinList = [i for i in get_pairs()]
        self.main_layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        for btn in CoinList:
            CoinButton = Button(text=f"{btn}", size_hint_y=None, height=40, on_press=lambda btn: self.open_graph(btn))
            self.main_layout.add_widget(CoinButton)

        self.scroll = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
        self.scroll.add_widget(self.main_layout)

    def open_graph(self, coin):
        self.run_CoinWindow = True

        self.Coin = Pair(name=coin.text)
        self.coin_start = StopableThread(target=start, args=(self.Coin,))
        self.coin_start.start()

        self.graph = GRAPH(coin=coin.text)
        self.scroll.clear_widgets()

        self.GraphCoin = GridLayout(rows=1, cols=1)
        self.GraphCoin.add_widget(self.graph.layout)
        self.scroll.add_widget(self.GraphCoin)

        self.update_start = StopableThread(target=self.graph.update_graph, args=(self.Coin.data,))
        self.update_start.start()

        self.is_stopped = StopableThread(target=self.close_graph)
        self.is_stopped.start()

        return self.scroll

    def close_graph(self):
        while True:
            if self.graph.stop:

                self.coin_start.stop()
                self.update_start.stop()
                self.is_stopped.stop()

                del self.Coin
                del self.graph
                del self.coin_start
                del self.update_start
                del self.is_stopped

                self.scroll.clear_widgets()
                self.scroll.add_widget(self.main_layout)
                return self.scroll

    def run(self):
        return self.scroll


class MyApp(App):
    def build(self):
        Window.size = Window.size
        return GRAPHlayout().run()


if __name__ == '__main__':
    MyApp().run()