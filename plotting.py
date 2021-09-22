import json
from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy_garden.graph import Graph, MeshLinePlot


class GRAPH(GridLayout):
    def __init__(self, coin, **kwargs):
        super().__init__(**kwargs)
        self.name = coin
        self.graph = Graph(xlabel='Time', ylabel='Price', x_ticks_minor=2,
                           x_ticks_major=8, y_ticks_major=8,
                           y_grid_label=True, x_grid_label=True, padding=5,
                           x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=0, ymax=100)

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(x, x * 2) for x in range(0, 101)]
        self.graph.add_plot(self.plot)

        self.layout = GridLayout(cols=1, rows=1)
        self.layout.add_widget(self.graph)

    def update_graph(self):
        while True:
            try:
                data = json.loads(f"{self.name}.json").get('data')
                data = sorted(data, reverse=False)
                self.graph.xmin = data[0][0]
                self.graph.ymin = data[0][1]
                self.graph.x_ticks_major = abs(data[0][0] - data[-1][0])
                self.graph.y_ticks_major = abs(data[0][1] - data[-1][1])
                # self.plot.points = [(info[0], info[1]) for info in data]
                self.graph.add_plot(self.plot)
            except:
                pass

    def run(self):
        return self.layout


class MyApp(App):
    def build(self):
        return GRAPH(coin='').run()


if __name__ == '__main__':
    MyApp().run()