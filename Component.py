from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Config import *


class MySlider(QSlider):
    """ReWrite for QSlider

    Control View Scale
    Due to slide time delay, start a timer. 

    Attributes:
        view: QGraphicsView对象
    """
    def __init__(self, view, *args, **kwargs):
        super(MySlider, self).__init__(*args, **kwargs)
        self.view = view
        self.last_val = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.scaleView)

    def scaleView(self):
        print('after value: ', self.value())
        self.view.scale(self.value()/self.last_val, self.value()/self.last_val)
        self.timer.stop()

    def mousePressEvent(self, e):
        """record last time value"""
        print('last value: ', self.value())
        self.last_val = self.value()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        print('value:', self.value())
        self.timer.start(500)


class Note(QMainWindow):
    """New a Note SubWindow

    new a window under activateNode

    Signals:
        note: close Note Window send note content
        noteChange: Note Window text Change
    """
    note = pyqtSignal(str)
    noteChange = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.boldCheck = True
        self.italicCheck = True
        self.underlineCheck = True

        self.toolbar = self.addToolBar('toolbar')

        bold_action = QAction('B', self)
        bold_action.triggered.connect(self.bold)
        self.toolbar.addAction(bold_action)

        skew_action = QAction('I', self)
        skew_action.triggered.connect(self.skew)
        self.toolbar.addAction(skew_action)

        underline_action = QAction('U', self)
        underline_action.triggered.connect(self.underline)
        self.toolbar.addAction(underline_action)

        self.textEdit = QTextEdit(self)
        self.setCentralWidget(self.textEdit)
        self.textEdit.textChanged.connect(self.text_changed)

        self.resize(*NOTE_SIZE)

    def changeFormat(self, fmt):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)

    def bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.boldCheck else QFont.Normal)
        self.changeFormat(fmt)
        self.boldCheck = not self.boldCheck

    def skew(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italicCheck)
        self.changeFormat(fmt)
        self.italicCheck = not self.italicCheck

    def underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.underlineCheck)
        self.changeFormat(fmt)
        self.underlineCheck = not self.underlineCheck

    def handle_addnote(self, x, y, note):
        self.move(x, y)
        self.textEdit.setText(note)
        if not self.isVisible():
            self.show()

    def handle_close(self):
        self.note.emit(self.textEdit.toPlainText())
        self.close()

    def text_changed(self):
        self.noteChange.emit()


class Link(QMainWindow):
    """New a Link Window

    new a Link Window under activateNode

    Signals:
        link: close Link Window send link content
        linkChange: Link Window text Change
    """
    link = pyqtSignal(str)
    linkChange = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)
        self.onMode = False

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.label = QLabel(self)
        self.label.setText('超链接')

        self.lineEdit = QLineEdit(self)

        vb = QVBoxLayout()
        vb.addWidget(self.label)
        vb.addWidget(self.lineEdit)

        w = QWidget()
        w.setLayout(vb)
        
        self.setCentralWidget(w)
        self.lineEdit.textChanged.connect(self.link_changed)

        self.resize(*LINK_SIZE)

    def handle_addLink(self, x, y, link):
        self.move(x, y)
        self.lineEdit.setText(link)
        if not self.isVisible():
            self.onMode = True
            self.show()

    def handle_close(self):
        if self.onMode:
            self.onMode = False
            self.link.emit(self.lineEdit.text())
            self.close()
        
    def link_changed(self):
        self.linkChange.emit()