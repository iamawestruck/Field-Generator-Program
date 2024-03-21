import types

from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
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


class ParametersGroupBox(QtWidgets.QWidget):
    parametersSignal = QtCore.Signal(float, float, float, float, float, float, float, float)

    def __init__(self):
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout = self.layout()

        self.xRange = VariableRangeWidget(Variables.X)
        self.yRange = VariableRangeWidget(Variables.Y)
        self.tRange = VariableRangeWidget(Variables.T)
        self.xRange.minInputBox.valueChanged.connect(self.updateParameters)
        self.xRange.maxInputBox.valueChanged.connect(self.updateParameters)
        self.yRange.minInputBox.valueChanged.connect(self.updateParameters)
        self.yRange.maxInputBox.valueChanged.connect(self.updateParameters)
        self.tRange.minInputBox.valueChanged.connect(self.updateParameters)
        self.tRange.maxInputBox.valueChanged.connect(self.updateParameters)
        self.layout.addWidget(self.xRange)
        self.layout.addWidget(self.yRange)
        self.layout.addWidget(self.tRange)
        self.tRange.hide()

        self.densityWidget = VariableSpinWidget("Density")
        self.densityWidget.inputBox.valueChanged.connect(self.updateParameters)
        self.lineLengthWidget = VariableSpinWidget("Line Length")
        self.lineLengthWidget.inputBox.valueChanged.connect(self.updateParameters)

        self.layout.addWidget(self.densityWidget)
        self.layout.addWidget(self.lineLengthWidget)

    def updateParameters(self):
        xmin = float(self.xRange.minInputBox.text())
        xmax = float(self.xRange.maxInputBox.text())
        ymin = float(self.yRange.minInputBox.text())
        ymax = float(self.yRange.maxInputBox.text())
        tmin = float(self.tRange.minInputBox.text())
        tmax = float(self.tRange.maxInputBox.text())
        density = float(self.densityWidget.inputBox.text())
        lineLength = float(self.lineLengthWidget.inputBox.text())
        self.parametersSignal.emit(xmin, xmax, ymin, ymax, tmin, tmax, density, lineLength)


class MplCanvas(FigureCanvasQTAgg):
    fig = None
    graphClickedSignal = QtCore.Signal(float, float)
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig=Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onGraphPress)

    def onGraphPress(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.graphClickedSignal.emit(event.xdata, event.ydata)

class GraphsGroupBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QtWidgets.QGridLayout())
        self.layout = self.layout()

        self.mainGraph = MplCanvas()
        self.mainGraph.graphClickedSignal.connect(self.graphSolution)
        self.mainGraph.setMinimumSize(400, 250)
        self.xParametricGraph = MplCanvas()
        self.xParametricGraph.setMaximumSize(350,120)
        self.xParametricGraph.setMinimumSize(350,120)
        self.yParametricGraph = MplCanvas()
        self.yParametricGraph.setMaximumSize(350,120)
        self.yParametricGraph.setMinimumSize(350,120)

        self.layout.addWidget(self.mainGraph, 0, 0, 2, 2)
        self.layout.addWidget(self.xParametricGraph, 2, 0, 1, 1)
        self.layout.addWidget(self.yParametricGraph, 2, 1, 1, 1)
        self.xParametricGraph.hide()
        self.yParametricGraph.hide()

        self.xEquation = (None, None)
        self.yEquation = (None, None)
        self.isStandard = True

        self.xmin = -10
        self.xmax = 10
        self.ymin = -10
        self.ymax = 10
        self.tmin = -10
        self.tmax = 10
        self.density = 1
        self.lineLength = 1

    @QtCore.Slot(float, float, float, float, float, float, float, float)
    def updateParameters(self, xmin, xmax, ymin, ymax, tmin, tmax, density, lineLength):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.tmin = tmin
        self.tmax = tmax
        self.density = density
        self.lineLength = lineLength
        self.graphField()

    @QtCore.Slot(Variables, str, types.LambdaType)
    def setEquation(self, variable, equationString, equationLambda):
        if variable == Variables.X:
            self.xEquation = (equationString, equationLambda)
        elif variable == Variables.Y:
            self.yEquation = (equationString, equationLambda)
        self.graphField()


    @QtCore.Slot(str)
    def removeEquation(self, equationString):
        if self.xEquation[0] == equationString:
            self.xEquation = (None, None)
            if not self.isStandard:
                self.clearGraphs()
        elif self.yEquation[0] == equationString:
            self.yEquation = (None, None)
        self.graphField()


    def graphField(self):
        self.clearGraphs()
        if self.isStandard:
            if self.yEquation[0] is not None:
                self.graphStandardField()
        else:
            if self.xEquation[0] is not None and self.yEquation[0] is not None:
                self.graphParametricField()

    @QtCore.Slot(float, float)
    def graphSolution(self, xinit, yinit):
        if self.isStandard:
            if self.yEquation[0] is not None:
                self.graphStandardSolution(xinit, yinit)
            else:
                self.clearGraphs()
        else:
            if self.xEquation[0] is not None and self.yEquation[0] is not None:
                self.graphParametricSolution(xinit, yinit)
            else:
                self.clearGraphs()

    def graphStandardField(self):
        x = np.linspace(self.xmin, self.xmax, int(self.density * 20))
        y = np.linspace(self.ymin, self.ymax, int(self.density * 20))
        X, Y = np.meshgrid(x, y)

        slopes = self.yEquation[1](X, Y)
        U = (1 / (1 + slopes ** 2) ** 0.5) * np.ones(X.shape)
        V = (1 / (1 + slopes ** 2) ** 0.5) * slopes

        self.mainGraph.axes.set_title("Slope Field Generator")
        scale = 50 / self.lineLength
        self.mainGraph.axes.cla()
        self.mainGraph.axes.quiver(X, Y, U, V, headlength=0, headwidth=1, color='deepskyblue', scale=scale)
        self.mainGraph.draw()

    def graphParametricField(self):
        x = np.linspace(self.xmin, self.xmax, int(self.density * 20))
        y = np.linspace(self.ymin, self.ymax, int(self.density * 20))
        X, Y = np.meshgrid(x, y)
        U = self.xEquation[1](X, Y)
        V = self.yEquation[1](X, Y)

        self.mainGraph.axes.set_title("Vector Field Generator")
        scale = 50 / self.lineLength
        self.mainGraph.axes.cla()
        self.mainGraph.axes.quiver(X, Y, U, V, headwidth=5, color='deepskyblue', scale=scale)
        self.mainGraph.draw()

    def graphStandardSolution(self, xinit, yinit):
        xstep, ystep = (xinit, yinit)
        X = []
        Y = []
        for i in range(2000000):
            X.append(xstep)
            Y.append(ystep)
            try:
                slope = self.yEquation[1](xstep, ystep)
            except ZeroDivisionError:
                break
            ystep += slope * 0.0005
            xstep += 0.0005
            if xstep > self.xmax or xstep < self.xmin or ystep > self.ymax or ystep < self.ymin:
                break
        for i in range(2000000):
            X.append(xstep)
            Y.append(ystep)
            try:
                slope = self.yEquation[1](xstep, ystep)
            except ZeroDivisionError:
                break
            ystep -= slope * 0.0005
            xstep -= 0.0005
            if xstep > self.xmax or xstep < self.xmin or ystep > self.ymax or ystep < self.ymin:
                break
        X = np.array(X)
        Y = np.array(Y)
        self.mainGraph.axes.plot(X, Y)
        self.mainGraph.draw()

    def graphParametricSolution(self, xinit, yinit):
        times = np.linspace(self.tmin, self.tmax, 500)
        solution = solve_ivp(lambda t, vars: [self.xEquation[1](vars[0], vars[1]), self.yEquation[1](vars[0], vars[1])], [self.tmin, self.tmax],
                             [xinit, yinit], t_eval=times)
        xvals = []
        yvals = []
        for i in range(len(solution.y[0])):
            x = solution.y[0][i]
            y = solution.y[1][i]
            if x > self.xmin and x < self.xmax and y > self.ymin and y < self.ymax:
                xvals.append(x)
                yvals.append(y)
        self.mainGraph.axes.plot(xvals, yvals)
        self.xParametricGraph.axes.plot(solution.t, solution.y[0], label="x(t)")
        self.yParametricGraph.axes.plot(solution.t, solution.y[1], label="y(t)")
        self.mainGraph.draw()
        self.xParametricGraph.draw()
        self.yParametricGraph.draw()

    def clearGraphs(self):
        self.mainGraph.axes.cla()
        self.mainGraph.draw()
        self.xParametricGraph.axes.cla()
        self.xParametricGraph.draw()
        self.yParametricGraph.axes.cla()
        self.yParametricGraph.draw()


class InputErrorDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("Error with entered equation, please try again.")
        self.okButton = QtWidgets.QPushButton("Ok")
        self.okButton.clicked.connect(self.close)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.okButton)
        self.setLayout(self.layout)
        self.setWindowTitle("Input Error")


class InputGroupBox(QtWidgets.QWidget):
    button = []
    arrow = 0
    mathCommands = {
        0: "pi",
        1: "sin",
        2: "cos",
        3: "e",
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
    lambdaEquationSignal = QtCore.Signal(str, types.LambdaType)

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
        func = self.inputBox.text()
        lambdaExpression = lambda x, y: eval(func, {}, {
            "x": x,
            "y": y,
            "e": np.e,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "arcsin": np.arcsin,
            "arccos": np.arccos,
            "arctan": np.arctan,
            "pi": np.pi
        })

        try:
            if type(lambdaExpression(1.0, 1.0)) is float or type(lambdaExpression(1.0, 1.0)) is np.float64:
                self.lambdaEquationSignal.emit(func, lambdaExpression)
            else:
                print(type(lambdaExpression(1.0, 1.0)))
                popup = InputErrorDialog()
                popup.exec()
        except Exception as err:
            popup = InputErrorDialog()
            popup.exec()


class EquationWidget(QtWidgets.QWidget):
    def __init__(self, equationString, equationLambda, isStandard):
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
        if isStandard:
            self.xButton.hide()
        self.setLayout(widgetLayout)


class EquationListWidget(QtWidgets.QWidget):

    setEquationSignal = QtCore.Signal(Variables, str, types.LambdaType)
    removeEquationSignal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.equationWidgets = {}
        self.xButtonGroup = QtWidgets.QButtonGroup()
        self.yButtonGroup = QtWidgets.QButtonGroup()
        layout = QtWidgets.QVBoxLayout()
        self.standardLabelWidget = QtWidgets.QLabel(" dy/dx ")
        self.parametricLabelWidget = QtWidgets.QLabel(" dx/dt  dy/dt ")
        self.parametricLabelWidget.hide()
        self.isStandard = True
        layout.addWidget(self.standardLabelWidget,
                         alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.parametricLabelWidget, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

    @QtCore.Slot(str, types.LambdaType)
    def addEquation(self, equationString, equationLambda):
        if equationString in self.equationWidgets.keys():
            return
        currentEquation = EquationWidget(equationString, equationLambda, self.isStandard)
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
        currentEquation = self.equationWidgets.pop(equationString)
        currentEquation.hide()
        layout = self.layout()
        layout.removeWidget(currentEquation)
        self.setLayout(layout)
        self.removeEquationSignal.emit(equationString)

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
        self.setEquationSignal.emit(Variables.X, equationString, equationLambda)

    def setYEquation(self, equationString, equationLambda):
        self.setEquationSignal.emit(Variables.Y, equationString, equationLambda)


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

class CentralWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.equationListGroupBox = EquationListGroupBox()
        self.graphsGroupBox = GraphsGroupBox()
        self.inputGroupBox = InputGroupBox()
        self.parametersGroupBox = ParametersGroupBox()

        self.layout = QtWidgets.QGridLayout()

        self.layout.addWidget(self.equationListGroupBox, 0, 0, 3, 1)
        self.layout.addWidget(self.graphsGroupBox, 0, 1, 3, 2)
        self.layout.addWidget(self.inputGroupBox, 3, 0, 1, 2)
        self.layout.addWidget(self.parametersGroupBox, 3, 2, 1, 1)

        self.equationListGroupBox.standardParametricWidget.parametricButton.clicked.connect(self.switchToParametric)
        self.equationListGroupBox.standardParametricWidget.standardButton.clicked.connect(self.switchToStandard)

        self.equationListGroupBox.equationListWidget.setEquationSignal.connect(self.graphsGroupBox.setEquation)
        self.equationListGroupBox.equationListWidget.removeEquationSignal.connect(self.graphsGroupBox.removeEquation)

        self.inputGroupBox.lambdaEquationSignal.connect(self.equationListGroupBox.equationListWidget.addEquation)

        self.parametersGroupBox.parametersSignal.connect(self.graphsGroupBox.updateParameters)

        self.equationListGroupBox.equationListWidget.addEquation("x+x", lambda x,y: x+x)
        self.equationListGroupBox.equationListWidget.addEquation("x+y", lambda x,y: x+y)

        self.setLayout(self.layout)

    def switchToParametric(self):
        self.layout.addWidget(self.equationListGroupBox, 0, 0, 3, 1)
        self.layout.addWidget(self.graphsGroupBox, 0, 1, 3, 2)
        self.layout.addWidget(self.inputGroupBox, 3, 0, 1, 2)
        self.layout.addWidget(self.parametersGroupBox, 3, 2, 1, 1)
        self.graphsGroupBox.yParametricGraph.show()
        self.graphsGroupBox.xParametricGraph.show()
        self.parametersGroupBox.tRange.show()
        self.equationListGroupBox.equationListWidget.parametricShowButtons()
        self.graphsGroupBox.isStandard = False
        self.equationListGroupBox.equationListWidget.isStandard = False
        self.graphsGroupBox.graphField()


    def switchToStandard(self):
        self.layout.addWidget(self.equationListGroupBox, 0, 0, 3, 1)
        self.layout.addWidget(self.graphsGroupBox, 0, 1, 3, 2)
        self.layout.addWidget(self.inputGroupBox, 3, 0, 1, 2)
        self.layout.addWidget(self.parametersGroupBox, 3, 2, 1, 1)
        self.graphsGroupBox.yParametricGraph.hide()
        self.graphsGroupBox.xParametricGraph.hide()
        self.parametersGroupBox.tRange.hide()
        self.equationListGroupBox.equationListWidget.standardHideButtons()
        self.graphsGroupBox.isStandard = True
        self.equationListGroupBox.equationListWidget.isStandard = True
        self.graphsGroupBox.graphField()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Field Generator")
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