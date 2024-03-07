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

class InputGroupBox(QtWidgets.QWidget):
    mathCommands = {
        0: "pi",
        1: "sin",
        2: "cos",
        3: "E",
        4: "+",
        5: "-",
        6: "/",
        7: "*",
    }
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        self.mathButtons = QtWidgets.QButtonGroup(self)
        self.arrowButtons = QtWidgets.QButtonGroup(self)

        self.mathButtonsGroup = QtWidgets.QWidget()
        self.arrowButtonsGroup = QtWidgets.QWidget()
        self.textBox = QtWidgets.QWidget()

        self.mathButtonsGroup.layout = QtWidgets.QHBoxLayout(self.mathButtonsGroup)
        self.arrowButtonsGroup.layout = QtWidgets.QHBoxLayout(self.arrowButtonsGroup)
        self.textBox.layout = QtWidgets.QHBoxLayout(self.textBox)

        for i in range(0,len(self.mathCommands)):
            mathbutton = QtWidgets.QPushButton(self.mathCommands[i])
            self.mathButtons.addButton(mathbutton, i)
            self.mathButtonsGroup.layout.addWidget(mathbutton)


            # self.button8 = QtWidgets.QPushButton("*")
        self.leftButton = QtWidgets.QPushButton("<--")
        self.rightButton = QtWidgets.QPushButton("-->")
        self.inputbox = QtWidgets.QLineEdit()


        # self.mathButtonsGroup.layout.addWidget(self.button1)

        self.arrowButtonsGroup.layout.addWidget(self.leftButton)
        self.arrowButtonsGroup.layout.addWidget(self.rightButton)

        self.textBox.layout.addWidget(self.inputbox)

        self.layout.addWidget(self.mathButtonsGroup)
        self.layout.addWidget(self.arrowButtonsGroup)
        self.layout.addWidget(self.textBox)

        #for i in range(0,8):
        self.mathButtons.idClicked.connect(lambda i :self.addText(i))
        # self.button1.clicked.connect(lambda: self.addText("pi"))


        self.inputbox.returnPressed.connect(lambda: self.close())

    def addText(self, text):
        self.inputbox.insert(self.mathCommands[text])

    #  def whenEnter(self):

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])



        widget = InputGroupBox()


        self.setCentralWidget(widget)

        self.show()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec()