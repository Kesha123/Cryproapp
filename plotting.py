from kivy.uix.relativelayout import RelativeLayout
from kivy_garden.graph import Graph as GRAPH, MeshLinePlot
from kivy.uix.label import Label
from kivy.uix.button import Button
import time


class Graph(RelativeLayout):
    def __init__(self, coin='', **kwargs):
        super().__init__(**kwargs)
        self.stop = False
        self.coin = coin
        self.graph = GRAPH(xlabel='Time', ylabel='Price', x_ticks_minor=1,
                           x_ticks_major=2, y_ticks_major=8,
                           y_grid_label=True, x_grid_label=True, padding=5,
                           x_grid=True, y_grid=True, xmin=0, xmax=59, ymin=0, ymax=100,
                           size_hint=(1, .9))

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = []
        self.graph.add_plot(self.plot)

        self.info = Label(text='', size_hint=(.9, .1), pos_hint={"right": 1, "top": 1}, markup=True)

        self.BackButton = Button(text="Back", size_hint=(.1, .1), pos_hint={"left": 1, "top": 1}, on_press=lambda x: self.stop_plotting(key='btn'))

        self.layout = RelativeLayout()
        self.layout.add_widget(self.BackButton)
        self.layout.add_widget(self.info)
        self.layout.add_widget(self.graph)

    def update_graph(self, data):
        while True:
            if data:
                self.graph.xmin = data[0][0]
                self.graph.ymax = max(data, key=lambda x: x[1])[1] + 10

                if min(data, key=lambda x: x[1])[1] - 10 >= 1:
                    self.graph.ymin = min(data, key=lambda x: x[1])[1] - 10

                elif 1 >= min(data, key=lambda x: x[1])[1] >= 0:
                    self.graph.ymax = min(data, key=lambda x: x[1])[1]*1.5
                    self.graph.ymin = min(data, key=lambda x: x[1])[1]*0.9

                self.plot.points = [(info[0], info[1]) for info in data]
                self.graph.add_plot(self.plot)
                self.info.text = f"[b]{data[0][3]}[/b]  {data[0][2]}:{data[-1][0]}  last price: [b]{data[-1][1]}$[/b]"

                time.sleep(1)

    def stop_plotting(self, key):
        if key == 'btn':
            self.stop = True

    def run(self):
        return self.layout

    def __delete__(self, instance):
        print("Delete plotting")
