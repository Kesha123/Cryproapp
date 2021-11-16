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

from kivy.event import *
from functools import partial

from plotting import Graph
from Pairs import Pair, start, get_pairs


class CoinApp(App):
    def build(self):
        Window.size = Window.size
        self.app = Build()
        return self.app.run()

    def update(self, number):
        self.app.bind_buttons(number)


application = CoinApp()


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


class MainWindow(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = RelativeLayout()
        self.main_layout.clear_widgets()

        self.button_size = Window.height*0.9//3
        self.CoinList = [i for i in get_pairs()][0:10]

        self.button_layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.button_layout.bind(minimum_height=self.button_layout.setter('height'))

        #self.button_list = [Button(text=f"{btn}", size_hint_y=None, height=self.button_size, on_press=lambda *a: application.app.open_graph(self.CoinList.index(btn))) for btn in self.CoinList]
        for i in self.CoinList:
            button = Button(text=f"{i}", size_hint_y=None, height=self.button_size, on_press=lambda *a: self.open_graph(i))
            self.button_layout.add_widget(button)

        #self.button_list = [i for i in self.CoinList]

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

    def open_graph(self, a):
        print(a)

    def search(self, name):
        self.button_layout.clear_widgets()
        self.scroll.clear_widgets()
        self.main_layout.clear_widgets()

        self.button_list.clear()
        self.button_list = [Button(text=btn, size_hint_y=None, height=self.button_size, on_press=lambda name: application.app.open_graph(btn)) for btn in self.CoinList if SequenceMatcher(None, btn.lower(), name.lower()).ratio() >= 0.3]
        for btn in self.button_list:
            self.button_layout.add_widget(btn)

        #self.button_list = [i for i in self.CoinList if SequenceMatcher(None, i.lower(), name.lower()).ratio() >= 0.3]

        if not self.button_list:
            self.no_matches = GridLayout(size_hint=(1, .9), size=(Window.width, Window.height), cols=1, rows=1)
            self.no_matches.add_widget(Label(text="No matches",))
            self.main_layout.add_widget(self.no_matches)
            self.main_layout.add_widget(self.search_layout)

        elif self.button_list:
            self.scroll.add_widget(self.button_layout)
            self.main_layout.add_widget(self.scroll)
            self.main_layout.add_widget(self.search_layout)

        #application.update(number=len(self.button_list))

    def reset(self):
        self.search_label.text = ""
        self.main_layout.clear_widgets()
        self.scroll.clear_widgets()
        self.button_layout.clear_widgets()

        self.button_list.clear()
        self.button_list = [Button(text=f"{btn}", size_hint_y=None, height=self.button_size, on_press=lambda name: application.app.open_graph(btn)) for btn in self.CoinList]
        for btn in self.button_list:
            self.button_layout.add_widget(btn)

        #self.button_list = [i for i in self.CoinList]

        self.scroll.add_widget(self.button_layout)
        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(self.search_layout)

        #application.update(number=len(self.button_list))


class Build(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = RelativeLayout()
        self.button_size = Window.height * 0.9 // 3

        self.main_window = MainWindow()
        self.connection_window = ConnectionErrorWindow().internet_layout
        self.main_layout.add_widget(self.main_window.main_layout)
        #self.bind_buttons(0)

    """def bind_buttons(self, number):
        print(self.main_window.button_list)
        for j in self.main_window.button_list[number:number+1]:
            button = Button(text=f"{j}", size_hint_y=None, height=self.button_size,
                            on_press=lambda name: self.open_graph(j))
            self.main_window.button_layout.add_widget(button)

        if number + 1 != len(self.main_window.button_list) + 1:
            self.bind_buttons(number+1)"""

    def open_graph(self, coin):
        self.main_layout.clear_widgets()
        print(coin)

        self.coin = Pair(name=coin)
        self.coin_start = StopableThread(target=start, args=(self.coin,))
        self.coin_start.start()

        self.graph = Graph(coin=coin)
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.graph.layout)

        self.update_start = StopableThread(target=self.graph.update_graph, args=(self.coin.data,))
        self.update_start.start()

        self.is_stopped = StopableThread(target=self.close_graph)
        self.is_stopped.start()

        return self.main_layout

    def close_graph(self):
        while True:
            if self.graph.stop:
                self.coin_start.stop()
                self.update_start.stop()
                self.is_stopped.stop()

                del self.coin
                del self.graph
                del self.coin_start
                del self.update_start
                del self.is_stopped

                self.main_layout.clear_widgets()
                self.main_layout.add_widget(self.main_window.main_layout)
                return self.main_layout

    def run(self):
        return self.main_layout


def main():
    application.run()


if __name__ == '__main__':
    main()