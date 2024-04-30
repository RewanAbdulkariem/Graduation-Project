import sys

from PyQt5 import QtWidgets, uic

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('App.ui', self) # Load the .ui file
        self.show() # Show the GUI

app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()

app.exec()