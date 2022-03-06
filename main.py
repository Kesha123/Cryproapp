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

from plotting import Graph
from memory_profiler import profile


class CoinApp(App):
    def build(self):
        Window.size = Window.size
        self.app = Build()
        return self.app.run()


application = CoinApp()


class StopableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StopableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self._delete = threading.Event

    def stop(self):
        print(f"{self.name} is stopped")
        self._stop.set()

    def delete(self):
        print(f"{self.name} is deleted")
        self._delete.set()

    def stopped(self):
        return self._stop.isSet()

    def __delete__(self, instance):
        print(f"Thread is deleted || {self.name}++")


class ConnectionErrorWindow(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.internet_layout = RelativeLayout()
        self.error_label = Label(text="No internet connection, try again", pos_hint={"center_x": 0.5, "center_y": 0.8})
        self.reload_button = Button(text="Reload", size_hint=(.2, .2), pos_hint={"center_x": 0.5, "center_y": 0.5}, on_press=lambda key: self.reload())
        self.internet_layout.add_widget(self.error_label)
        self.internet_layout.add_widget(self.reload_button)

    def __del__(self):
        print("Delete internet window")

    def reload(self):
        if check_internet_connection():
            self.internet_layout.clear_widgets()
            application.run()
        else:
            return self


def check_internet_connection():
    try:
        from Pairs import get_pairs
    except:
        return False
    else:
        return True


class MainWindow(RelativeLayout):
    def __init__(self, internet, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = RelativeLayout()

        if internet:
            from Pairs import get_pairs

            self.button_size = Window.height*0.9//3
            self.CoinList = [i for i in get_pairs()]

            self.button_layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
            self.button_layout.bind(minimum_height=self.button_layout.setter('height'))

            for btn in self.CoinList:
                CoinButton = Button(text=f"{btn}", size_hint_y=None, height=self.button_size,
                                    on_press=lambda btn: application.app.open_graph(btn))
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
            self.connection_window = ConnectionErrorWindow().internet_layout
            self.main_layout.add_widget(self.connection_window)

    def search(self, name):
        self.button_layout.clear_widgets()
        self.scroll.clear_widgets()
        self.main_layout.clear_widgets()

        for btn in self.CoinList:
            if SequenceMatcher(None, btn.lower(), name.lower()).ratio() >= 0.6:
                CoinButton = Button(text=f"{btn}", size_hint_y=None, height=self.button_size,
                                    on_press=lambda btn: application.app.open_graph(btn))
                self.button_layout.add_widget(CoinButton)

        if not self.button_layout.children:
            self.no_matches = GridLayout(size_hint=(1, .9), size=(Window.width, Window.height), cols=1, rows=1)
            self.no_matches.add_widget(Label(text="No matches",))
            self.main_layout.add_widget(self.no_matches)
            self.main_layout.add_widget(self.search_layout)

        elif self.button_layout.children:
            self.scroll.add_widget(self.button_layout)
            self.main_layout.add_widget(self.scroll)
            self.main_layout.add_widget(self.search_layout)

    def reset(self):
        self.search_label.text = ""
        self.main_layout.clear_widgets()
        self.scroll.clear_widgets()
        self.button_layout.clear_widgets()

        for btn in self.CoinList:
            CoinButton = Button(text=f"{btn}", size_hint_y=None, height=self.button_size,
                                on_press=lambda btn: application.app.open_graph(btn))
            self.button_layout.add_widget(CoinButton)

        self.scroll.add_widget(self.button_layout)
        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(self.search_layout)


class Build(RelativeLayout, object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.internet = check_internet_connection()

        self.main_layout = RelativeLayout()
        self.main_window = MainWindow(internet=self.internet)
        self.main_layout.add_widget(self.main_window.main_layout)

    @profile
    def open_graph(self, name):
        from Pairs import start, Pair
        self.main_layout.clear_widgets()

        self.coin = Pair(name=name.text)
        self.graph = Graph(coin=name)

        self.coin_start = StopableThread(target=start, args=(self.coin,), name="Collecting information thread")
        self.coin_start.start()

        self.update_start = StopableThread(target=self.graph.update_graph, args=(self.coin.data,), name="Plotting thread")
        self.update_start.start()

        self.is_stopped = StopableThread(target=self.close_graph, name="Stop thread")
        self.is_stopped.start()

        self.main_layout.add_widget(self.graph.layout)

        return self.main_layout

    @profile
    def close_graph(self):
        while True:
            if self.graph.stop:
                self.main_layout.clear_widgets()
                self.coin.unsubscribe = True

                self.coin_start.stop()
                self.update_start.stop()
                self.is_stopped.stop()
                print("\n")
                self.coin.__delete__(self.coin)
                self.graph.__delete__(self.graph)
                print("\n")
                self.coin_start.__delete__(self.coin_start)
                self.update_start.__delete__(self.update_start)
                self.is_stopped.__delete__(self.is_stopped)
                print("\n")
                print(self.coin)
                print(self.graph)

                self.main_layout.add_widget(self.main_window.main_layout)
                return self.main_layout

    def run(self):
        return self.main_layout


def main():
    application.run()


if __name__ == '__main__':
    main()