from PySide6.QtWidgets import QWidget, QGridLayout
import pyqtgraph as pg


class MultiPlanarWidget(QWidget):
    """Class unused in project, but may be useful in the future"""
    def __init__(self):
        super().__init__()

        self.left_top_widget = pg.PlotWidget()
        self.right_top_widget = pg.PlotWidget()
        self.left_bottom_widget = pg.PlotWidget()
        self.right_bottom_widget = QWidget()
        self.__set_layout()

    def __set_layout(self):
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.left_top_widget, 0, 0)
        layout.addWidget(self.right_top_widget, 0, 1)
        layout.addWidget(self.left_bottom_widget, 1, 0)
        layout.addWidget(self.right_bottom_widget, 1, 1)


class ProjectionArea(pg.PlotWidget):
    def __init__(self, **kargs):
        super().__init__(**kargs)
