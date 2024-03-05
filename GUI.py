from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import sys
import matplotlib
matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvasQTAgg):
    fig = None
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig=Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class inputGroupBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        self.mathButtons = QtWidgets.QWidget()
        self.textBox = QtWidgets.QWidget()

        self.mathButtons.layout = QtWidgets.QHBoxLayout(self.mathButtons)
        self.textBox.layout = QtWidgets.QHBoxLayout(self.textBox)

        self.button1 = QtWidgets.QPushButton("Pie")
        self.button2 = QtWidgets.QPushButton("Sign")
        self.button3 = QtWidgets.QPushButton("Co-sign")
        self.button4 = QtWidgets.QPushButton("E")
        self.inputbox = QtWidgets.QLineEdit()

        self.mathButtons.layout.addWidget(self.button1)
        self.mathButtons.layout.addWidget(self.button2)
        self.mathButtons.layout.addWidget(self.button3)
        self.mathButtons.layout.addWidget(self.button4)
        self.textBox.layout.addWidget(self.inputbox)

        self.layout.addWidget(self.mathButtons)
        self.layout.addWidget(self.textBox)
        #
        # self.button1.idClicked.connect(lambda i: self.boardNumberedColoredButtonClicked(i+2, "red"))
        # self.button2.idClicked.connect(lambda i: self.boardNumberedColoredButtonClicked(i+2, "yellow"))
        # self.button3.idClicked.connect(lambda i: self.boardNumberedColoredButtonClicked(12-i, "green"))
        # self.button4.idClicked.connect(lambda i: self.boardNumberedColoredButtonClicked(12-i, "blue"))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])



        widget = inputGroupBox()


        self.setCentralWidget(widget)

        self.show()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()