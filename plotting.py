from kivy.uix.gridlayout import GridLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.uix.label import Label
from kivy.uix.button import Button
import time


class GRAPH(GridLayout):
    def __init__(self, coin, **kwargs):
        super().__init__(**kwargs)
        self.name = coin
        self.graph = Graph(xlabel='Time', ylabel='Price', x_ticks_minor=1,
                           x_ticks_major=2, y_ticks_major=8,
                           y_grid_label=True, x_grid_label=True, padding=5,
                           x_grid=True, y_grid=True, xmin=0, xmax=59, ymin=0, ymax=100)

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = []
        self.graph.add_plot(self.plot)

        self.info = Label(text='')

        self.BackButton = Button(text="Back", on_press=lambda x: self.stop_plotting(key='btn'))
        self.stop = False

        self.layout = GridLayout(cols=1, rows=3)
        self.layout.add_widget(self.BackButton)
        self.layout.add_widget(self.info)
        self.layout.add_widget(self.graph)

    def update_graph(self, data):
        while True:
            if data:
                self.graph.xmin = data[0][0]
                self.graph.ymax = max(data, key=lambda x: x[1])[1] + 10
                self.graph.ymin = min(data, key=lambda x: x[1])[1] - 10

                self.plot.points = [(info[0], info[1]) for info in data]
                self.graph.add_plot(self.plot)
                self.info.text = f"{data[0][-1]} \nlast price: {data[-1][1]}$"

                time.sleep(1)

    def stop_plotting(self, key):
        if key == 'btn':
            self.stop = True

    def run(self):
        return self.layout
