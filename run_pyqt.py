# Run the PyQt5 UI (uses the Main class defined in submission/part3_pyqt5.py)
import sys
from PyQt5 import QtWidgets
from submission.part3_pyqt5 import Main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())
