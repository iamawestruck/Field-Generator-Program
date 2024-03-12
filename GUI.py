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
    button = []
    arrow = 0
    mathCommands = {
        0: "pi",
        1: "sin",
        2: "cos",
        3: "E",
        4: "+",
        5: "-",
        6: "/",
        7: "*",
        8: "tan",
        9: "arctan",
        10: "arcsin",
        11: "arccos",
        12: "^",
        13: "(",
        14: ")",
        15: "%",
    }

    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.mathButtons = QtWidgets.QButtonGroup(self)
        self.arrowButtons = QtWidgets.QButtonGroup(self)

        self.mathButtonsWidget = QtWidgets.QWidget()
        self.arrowButtonsWidget = QtWidgets.QWidget()
        self.textBox = QtWidgets.QWidget()

        self.mathButtonsWidget.layout = QtWidgets.QHBoxLayout(self.mathButtonsWidget)
        self.arrowButtonsWidget.layout = QtWidgets.QHBoxLayout(self.arrowButtonsWidget)
        self.textBox.layout = QtWidgets.QHBoxLayout(self.textBox)

        for i in range(0,8):
            mathbutton = QtWidgets.QPushButton(self.mathCommands[i])
            self.button.append(mathbutton)
            self.mathButtons.addButton(mathbutton, i)
            self.mathButtonsWidget.layout.addWidget(mathbutton)

            # self.button8 = QtWidgets.QPushButton("*")
        self.leftButton = QtWidgets.QPushButton("<--")
        self.rightButton = QtWidgets.QPushButton("-->")
        self.inputBox = QtWidgets.QLineEdit()

        # self.mathButtonsWidget.layout.addWidget(self.button1)
        self.arrowButtonsWidget.layout.addWidget(self.leftButton)
        self.arrowButtonsWidget.layout.addWidget(self.rightButton)
        self.textBox.layout.addWidget(self.inputBox)

        self.layout.addWidget(self.mathButtonsWidget)
        self.layout.addWidget(self.arrowButtonsWidget)
        self.layout.addWidget(self.textBox)

        # for i in range(0,8):
        self.mathButtons.idClicked.connect(lambda t: self.addText(t))
        self.leftButton.clicked.connect(lambda: self.shiftCommands(-1))
        self.rightButton.clicked.connect(lambda: self.shiftCommands(1))
        self.inputBox.returnPressed.connect(lambda: self.enterData())

    def addText(self, text):
        self.inputBox.insert(self.mathCommands[text])

    def shiftCommands(self, movement):

        if movement == 1:
            self.arrow += 1
        if movement == -1:
            self.arrow -= 1

        if self.arrow < 0:
            self.arrow = 0
        elif self.arrow > (len(self.mathCommands)/8)-1:
            self.arrow = (len(self.mathCommands)/8)-1
        else:
            for i in range(len(self.button)):
                self.button[i].setText(self.mathCommands[i + (8 * self.arrow)])

    def enterData(self):
        self.inputBox



    #  def whenEnter(self):

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
        self.standardLabelWidget.hide()
        layout.addWidget(self.standardLabelWidget,
                         alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
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

    def standardHideButtons(self):
        self.parametricLabelWidget.hide()
        self.standardLabelWidget.show()
        for value in self.equationWidgets.values():
            value.xButton.hide()

    def parametricShowButtons(self):
        self.standardLabelWidget.hide()
        self.parametricLabelWidget.show()
        for value in self.equationWidgets.values():
            value.xButton.show()

class StandardParametricWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.standardButton = QtWidgets.QPushButton("Standard")
        self.parametricButton = QtWidgets.QPushButton("Parametric")
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(self.standardButton, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        widgetLayout.addWidget(self.parametricButton, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.setLayout(widgetLayout)



class EquationListGroupBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.equationListWidget = EquationListWidget()
        self.standardParametricWidget = StandardParametricWidget()
        self.standardParametricWidget.standardButton.clicked.connect(self.equationListWidget.standardHideButtons)
        self.standardParametricWidget.parametricButton.clicked.connect(self.equationListWidget.parametricShowButtons)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.equationListWidget)
        layout.addWidget(self.standardParametricWidget,alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
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


        widget = InputGroupBox()


        self.setCentralWidget(widget)

        self.show()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec()