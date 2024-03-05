from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import sys
import matplotlib
matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig=Figure(figsize=(width,height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class EquationWidget(QtWidgets.QWidget):
    def __init__(self, equationString, equationLambda):
        super().__init__()
        self.equationString = equationString
        self.equationLambda = equationLambda
        self.xButton = QtWidgets.QRadioButton()
        self.yButton = QtWidgets.QRadioButton()
        self.buttons = QtWidgets.QWidget()
        self.buttons.layout = QtWidgets.QHBoxLayout()
        self.buttons.layout.addWidget(self.xButton)
        self.buttons.layout.addWidget(self.yButton)
        self.buttons.setLayout(self.buttons.layout)
        self.equationLabel = QtWidgets.QLabel()
        self.equationLabel.setText(equationString)
        self.deleteButton = QtWidgets.QPushButton("-")
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(self.buttons, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        widgetLayout.addWidget(self.equationLabel)
        widgetLayout.addWidget(self.deleteButton, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        # self.xButton.hide()
        self.setLayout(widgetLayout)


class EquationListWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.equationWidgets = {}
        self.xButtonGroup = QtWidgets.QButtonGroup()
        self.yButtonGroup = QtWidgets.QButtonGroup()
        layout = QtWidgets.QVBoxLayout()
        self.standardLabelWidget = QtWidgets.QLabel(" dy/dx ")
        self.parametricLabelWidget = QtWidgets.QLabel(" dx/dt  dy/dt ")
        layout.addWidget(self.parametricLabelWidget, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

    def addEquation(self, equationString, equationLambda):
        currentEquation = EquationWidget(equationString, equationLambda)
        currentEquation.deleteButton.clicked.connect(lambda: self.removeEquation(equationString))
        self.equationWidgets[equationString] = currentEquation
        self.xButtonGroup.addButton(currentEquation.xButton)
        self.yButtonGroup.addButton(currentEquation.yButton)
        layout = self.layout()
        layout.addWidget(currentEquation, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def removeEquation(self, equationString):
        if equationString not in self.equationWidgets.keys():
            return
        currentEquation = self.equationWidgets[equationString]
        currentEquation.hide()
        layout = self.layout()
        layout.removeWidget(currentEquation)
        self.setLayout(layout)


class EquationListGroupBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.equationListWidget = EquationListWidget()
        self.standardParametricWidget = None
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.equationListWidget)
        # layout.addWidget(self.standardParametricWidget)
        self.setLayout(layout)
        self.show()

    def addEquation(self, equationString, equationLambda):
        self.equationListWidget.addEquation(equationString, equationLambda)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # sc = MplCanvas(self, width=5, height=4, dpi=100)
        # sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        # self.setCentralWidget(sc)

        self.equationListGroupBox = EquationListGroupBox()
        self.equationListGroupBox.addEquation("x+x", lambda x,y: x+x)
        self.equationListGroupBox.addEquation("x+y", lambda x,y: x+y)
        self.equationListGroupBox.addEquation("x+y^2", lambda x, y: x + y*y)
        self.equationListGroupBox.addEquation("x+y*2", lambda x, y: x + y*2)
        self.setCentralWidget(self.equationListGroupBox)
        self.show()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()