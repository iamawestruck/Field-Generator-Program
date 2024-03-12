from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import sys
from enum import Enum
import matplotlib
matplotlib.use('Qt5Agg')


class Variables(Enum):
    X = 'x'
    Y = 'y'
    T = 't'


class MplCanvas(FigureCanvasQTAgg):
    fig = None
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig=Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setMinimumSize(200, 150)


class VariableSpinWidget(QtWidgets.QWidget):
    def __init__(self, variable):
        super().__init__()

        self.variableLabel = QtWidgets.QLabel(variable + ":")
        self.inputBox = QtWidgets.QDoubleSpinBox()
        self.inputBox.setValue(1)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout = self.layout()
        self.layout.addWidget(self.variableLabel, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.inputBox, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


class VariableRangeWidget(QtWidgets.QWidget):
    def __init__(self, variable):
        super().__init__()

        self.variableLabel = QtWidgets.QLabel(variable.value + ":")

        self.minInputBox = QtWidgets.QDoubleSpinBox()
        self.minInputBox.setMinimum(-1000000000)
        self.minInputBox.setMaximum(1000000000)
        self.minInputBox.setValue(-10)

        self.maxInputBox = QtWidgets.QDoubleSpinBox()
        self.maxInputBox.setMinimum(-1000000000)
        self.maxInputBox.setMaximum(1000000000)
        self.maxInputBox.setValue(10)


        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout = self.layout()
        self.layout.addWidget(self.variableLabel, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.minInputBox, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(QtWidgets.QLabel("-"), alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.maxInputBox, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


class GraphsGroupBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout = self.layout()

        self.mainGraph = MplCanvas()
        self.xParametricGraph = MplCanvas()
        self.yParametricGraph = MplCanvas()
        self.layout.addWidget(self.mainGraph)
        self.layout.addWidget(self.xParametricGraph)
        self.layout.addWidget(self.yParametricGraph)
        self.xParametricGraph.hide()
        self.yParametricGraph.hide()

        self.xRange = VariableRangeWidget(Variables.X)
        self.yRange = VariableRangeWidget(Variables.Y)
        self.tRange = VariableRangeWidget(Variables.T)
        self.layout.addWidget(self.xRange)
        self.layout.addWidget(self.yRange)
        self.layout.addWidget(self.tRange)
        self.tRange.hide()

        self.densityWidget = VariableSpinWidget("Density")
        self.lineLengthWidget = VariableSpinWidget("Line Length")
        self.layout.addWidget(self.densityWidget)
        self.layout.addWidget(self.lineLengthWidget)


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
        self.xButton.hide()
        self.setLayout(widgetLayout)


class EquationListWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.equationWidgets = {}
        self.xEquation, self.yEquation = ((None, None), (None, None))
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
        currentEquation.xButton.clicked.connect(lambda: self.setXEquation(equationString, equationLambda))
        currentEquation.yButton.clicked.connect(lambda: self.setYEquation(equationString, equationLambda))
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
        if equationString in self.yEquation:
            self.yEquation = (None, None)
        if equationString in self.xEquation:
            self.xEquation = (None, None)
        currentEquation = self.equationWidgets[equationString]
        currentEquation.hide()
        layout = self.layout()
        layout.removeWidget(currentEquation)
        self.setLayout(layout)

    def standardHideButtons(self):
        self.parametricLabelWidget.hide()
        self.standardLabelWidget.show()
        self.xEquation = None
        for value in self.equationWidgets.values():
            value.xButton.hide()

    def parametricShowButtons(self):
        self.standardLabelWidget.hide()
        self.parametricLabelWidget.show()
        for value in self.equationWidgets.values():
            value.xButton.show()

    def setXEquation(self, equationString, equationLambda):
        self.xEquation = (equationString, equationLambda)

    def setYEquation(self, equationString, equationLambda):
        self.yEquation = (equationString, equationLambda)


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
        layout.addWidget(self.standardParametricWidget, alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
        self.setLayout(layout)
        self.show()

    def addEquation(self, equationString, equationLambda):
        self.equationListWidget.addEquation(equationString, equationLambda)

class CentralWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.equationListGroupBox = EquationListGroupBox()
        self.graphsGroupBox = GraphsGroupBox()
        self.inputGroupBox = InputGroupBox()

        self.layout = QtWidgets.QGridLayout()

        self.layout.addWidget(self.equationListGroupBox, 0, 0, 3, 1)
        self.layout.addWidget(self.graphsGroupBox, 0, 1, 3, 1)
        self.layout.addWidget(self.inputGroupBox, 3, 0, 1, 2)

        self.equationListGroupBox.standardParametricWidget.parametricButton.clicked.connect(self.switchToParametric)
        self.equationListGroupBox.standardParametricWidget.standardButton.clicked.connect(self.switchToStandard)

        self.equationListGroupBox.addEquation("x+x", lambda x,y: x+x)

        self.setLayout(self.layout)

    def switchToParametric(self):
        self.layout.addWidget(self.equationListGroupBox, 0, 0, 3, 1)
        self.layout.addWidget(self.graphsGroupBox, 0, 1, 4, 1)
        self.layout.addWidget(self.inputGroupBox, 3, 0, 2, 1)
        self.graphsGroupBox.yParametricGraph.show()
        self.graphsGroupBox.xParametricGraph.show()
        self.graphsGroupBox.tRange.show()
        self.equationListGroupBox.equationListWidget.parametricShowButtons()

    def switchToStandard(self):
        self.layout.addWidget(self.equationListGroupBox, 0, 0, 3, 1)
        self.layout.addWidget(self.graphsGroupBox, 0, 1, 3, 1)
        self.layout.addWidget(self.inputGroupBox, 3, 0, 1, 2)
        self.graphsGroupBox.yParametricGraph.hide()
        self.graphsGroupBox.xParametricGraph.hide()
        self.graphsGroupBox.tRange.hide()
        self.equationListGroupBox.equationListWidget.standardHideButtons()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # sc = MplCanvas(self, width=5, height=4, dpi=100)
        # sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        # self.setCentralWidget(sc)

        # self.equationListGroupBox = EquationListGroupBox()
        # self.equationListGroupBox.addEquation("x+x", lambda x,y: x+x)
        # self.equationListGroupBox.addEquation("x+y", lambda x,y: x+y)
        # self.equationListGroupBox.addEquation("x+y^2", lambda x, y: x + y*y)
        # self.equationListGroupBox.addEquation("x+y*2", lambda x, y: x + y*2)
        # self.setCentralWidget(self.equationListGroupBox)

        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)

        self.show()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec()