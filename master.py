from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu
import sqlite3
import sys

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle('PixelKalpak')
        self.setGeometry(300, 300, 400, 300)

def start():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

if __name__ == '__main__':
    start()
