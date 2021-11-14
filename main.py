import threading
from difflib import SequenceMatcher

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.label import Label

from plotting import GRAPH


class StopableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StopableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class ConnectionErrorWindow(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.internet_layout = RelativeLayout()
        self.error_label = Label(text="No internet connection, try again", pos_hint={"center_x": 0.5, "center_y": 0.8})
        self.reload_button = Button(text="Reload", size_hint=(.2, .2), pos_hint={"center_x": 0.5, "center_y": 0.5}, on_press=lambda key: self.reload())
        self.internet_layout.add_widget(self.error_label)
        self.internet_layout.add_widget(self.reload_button)

    @staticmethod
    def reload():
        main()


class GRAPHLayout(RelativeLayout):

    @staticmethod
    def check_internet():
        try:
            from Pairs import Pair, start, get_pairs
            return True
        except:
            return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = RelativeLayout()

        if self.check_internet():
            from Pairs import get_pairs

            self.main_layout.clear_widgets()
            print(self.main_layout.children)

            self.button_size = Window.height*0.9//3
            self.CoinList = [i for i in get_pairs()]

            self.button_layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
            self.button_layout.bind(minimum_height=self.button_layout.setter('height'))

            for btn in self.CoinList:
                CoinButton = Button(text=f"{btn}", size_hint_y=None, height=self.button_size, on_press=lambda btn: self.open_graph(btn))
                self.button_layout.add_widget(CoinButton)

            self.scroll = ScrollView(size_hint=(1, .9), size=(Window.width, Window.height))
            self.scroll.add_widget(self.button_layout)

            self.search_layout = RelativeLayout()
            self.search_label = TextInput(multiline=False, size_hint=(.8, .1), pos_hint={"left": 1, "top": 1})
            self.search_button = Button(text="Search", size_hint=(.1, .1), pos_hint={"right": .9, "top": 1}, on_press=lambda name: self.search(self.search_label.text))
            self.reset_button = Button(text="Reset", size_hint=(.1, .1), pos_hint={"right": 1, "top": 1}, on_press=lambda key: self.reset())
            self.search_layout.add_widget(self.search_label)
            self.search_layout.add_widget(self.search_button)
            self.search_layout.add_widget(self.reset_button)

            self.main_layout.add_widget(self.scroll)
            self.main_layout.add_widget(self.search_layout)

        else:
            self.main_layout.clear_widgets()
            self.No_internet = ConnectionErrorWindow()
            self.main_layout.add_widget(self.No_internet.internet_layout)

    def open_graph(self, coin):
        from Pairs import Pair, start
        self.main_layout.clear_widgets()

        self.Coin = Pair(name=coin.text)
        self.coin_start = StopableThread(target=start, args=(self.Coin,))
        self.coin_start.start()

        self.GraphCoin = GridLayout(rows=1, cols=1)
        self.graph = GRAPH(coin=coin.text)
        self.GraphCoin.add_widget(self.graph.layout)
        self.main_layout.add_widget(self.GraphCoin)

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

                self.main_layout.clear_widgets()
                self.main_layout.add_widget(self.scroll)
                self.main_layout.add_widget(self.search_layout)
                return self.main_layout

    def search(self, name):
        self.button_layout.clear_widgets()
        self.scroll.clear_widgets()
        self.main_layout.remove_widget(self.scroll)

        cnt = 0
        for btn in self.CoinList:
            if SequenceMatcher(None, btn.lower(), name.lower()).ratio() >= 0.3:
                CoinButton = Button(text=f"{btn}", size_hint_y=None, height=self.button_size, on_press=lambda btn: self.open_graph(btn))
                self.button_layout.add_widget(CoinButton)
                cnt += 1

        if cnt == 0:
            self.no_matches = GridLayout(size_hint=(1, .9), size=(Window.width, Window.height), cols=1, rows=1)
            self.no_matches.add_widget(Label(text="No matches",))
            self.main_layout.add_widget(self.no_matches)

        elif cnt > 0:
            self.main_layout.clear_widgets()
            self.scroll.add_widget(self.button_layout)
            self.main_layout.add_widget(self.scroll)
            self.main_layout.add_widget(self.search_layout)

    def reset(self):
        self.search_label.text = ""
        self.main_layout.clear_widgets()
        self.scroll.clear_widgets()
        self.button_layout.clear_widgets()

        for btn in self.CoinList:
            CoinButton = Button(text=f"{btn}", size_hint_y=None, height=self.button_size, on_press=lambda btn: self.open_graph(btn))
            self.button_layout.add_widget(CoinButton)

        self.scroll.add_widget(self.button_layout)
        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(self.search_layout)

    def run(self):
        return self.main_layout


class MyApp(App):
    def build(self):
        Window.size = Window.size
        return GRAPHLayout().run()


def main():
    MyApp().run()


if __name__ == '__main__':
    main()