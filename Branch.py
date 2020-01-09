from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys


class Branch(QGraphicsLineItem):
    """Rewrite QGraphicsLineItem"""
    def __init__(self, *args, **kwargs):
        super(Branch, self).__init__(*args, **kwargs)

        self.srcNode = None
        self.dstNode = None
        self.width = 2
        self.color = Qt.darkBlue
        self.offsetScale = 0.4
        self.setZValue(-1)

    def adjust(self):
        offset = self.offsetScale * self.srcNode.sceneBoundingRect().width()
        p1_x = self.srcNode.sceneBoundingRect().center().x() + offset
        p1_y = self.srcNode.sceneBoundingRect().center().y()
        p1 = QPointF(p1_x, p1_y)

        p2_x = self.dstNode.sceneBoundingRect().x()
        p2_y = self.dstNode.sceneBoundingRect().center().y()
        p2 = QPointF(p2_x, p2_y)
        self.setLine(QLineF(p1, p2))