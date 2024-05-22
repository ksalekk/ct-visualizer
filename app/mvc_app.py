from PySide6.QtWidgets import QApplication
from app.model.model import Model
from app.views.main_window import MainWindow
from app.controllers.main_controller import MainController
from app.views.projection_view import ProjectionWidget


class MvcApp(QApplication):
    def __init__(self, sys_argv):
        super(MvcApp, self).__init__(sys_argv)

        model = Model()
        projections = ProjectionWidget(), ProjectionWidget(), ProjectionWidget()

        main_controller = MainController(self, model, projections)
        main_view = MainWindow(main_controller)
        main_controller.set_main_window(main_view)

        main_view.show()
