import os

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QToolBar, QFileDialog, QMenuBar, QMainWindow, QWidget, QTabWidget, QStyle, QPushButton

from app.helpers.interfaces import EventsHandler


class MainWindow(QMainWindow):
    """Class that represents main window in app."""

    def __init__(self, controller: EventsHandler):
        super().__init__()
        self.controller = controller

        self.__menubar_setup()
        self.toolbar = self.__toolbar_setup()

        self.setGeometry(100, 60, 1100, 600)
        self.setWindowTitle("CT Viewer")
        self.setWindowIcon(QIcon("resources/medical.png"))

    def set_working_area(self, xy: QWidget, xz: QWidget, yz: QWidget):
        """Get QWidget elements as parameters and set it as projection widgets.
        Every projection widget has own tab."""
        tabs = QTabWidget(self)
        self.setCentralWidget(tabs)

        tabs.addTab(xy, "Axial")
        tabs.addTab(xz, "Coronal")
        tabs.addTab(yz, "Sagittal")

        # multi_tab = MultiPlanarWidget()
        # tabs.addTab(multi_tab, "Orthographic Projection")

    def show_toolbar(self):
        """Enable toolbar"""
        self.toolbar.setParent(self)
        self.addToolBar(self.toolbar)

    def display_alert(self, text):
        """Display alert to user"""
        pass

    def __open_files(self):
        """Get directory path from user and send it to controller"""
        files = QFileDialog.getExistingDirectory(self, "Open file", os.getcwd())
        self.controller.load_model_handle(files)

    def __menubar_setup(self):
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        open_file_action = file_menu.addAction("Open File")
        open_file_action.triggered.connect(self.__open_files)

        exit_menu = menubar.addMenu("Exit")
        exit_action = exit_menu.addAction("Exit")
        exit_action.triggered.connect(self.controller.quit_app_handle)

        self.setMenuBar(menubar)

    def __toolbar_setup(self):
        toolbar = QToolBar()
        style = self.style()

        open_file_action = QAction(text="Open File", parent=toolbar,
                                   icon=style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        open_file_action.triggered.connect(self.__open_files)
        toolbar.addAction(open_file_action)
        toolbar.addSeparator()

        roi_mode_button = QPushButton(parent=toolbar,
                                      icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        roi_mode_button.setCheckable(True)
        roi_mode_button.clicked.connect(self.controller.roi_mode_handle)
        toolbar.addWidget(roi_mode_button)

        histogram_mode_button = QPushButton(parent=toolbar,
                                            icon=style.standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        histogram_mode_button.setCheckable(True)
        histogram_mode_button.clicked.connect(self.controller.histogram_mode_handle)
        toolbar.addWidget(histogram_mode_button)

        return toolbar
