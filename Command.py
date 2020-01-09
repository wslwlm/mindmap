from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys
from Config import *


class Context():
    """context for Command"""
    def __init__(self):
        self.m_scene = None
        self.m_activateNode = None
        self.m_nodeList = None
        self.m_pos = None
        self.m_color = None
        self.m_textColor = None


class InsertNodeCommand(QUndoCommand):
    """insert node"""
    def __init__(self, context, *args, **kwargs):
        super(InsertNodeCommand, self).__init__(*args, **kwargs)

        self.context = context

        self.node = self.context.m_scene.nodeFactory()
        self.node.x, self.node.y = self.context.m_pos
        self.node.num = len(self.context.m_scene.NodeList) + 1
        if self.context.m_activateNode.m_level == MainThemeLevel:
            self.node.setNodeLevel(SecondThemeLevel)
        else:
            self.node.setNodeLevel(ThirdThemeLevel)
            
    def undo(self):
        self.context.m_scene.NodeList.remove(self.node)
        self.context.m_activateNode.sonNode.remove(self.node)
        self.node.parentNode = None

        self.context.m_scene.removeBranch(self.node)
        self.context.m_scene.removeItem(self.node)

        if len(self.context.m_activateNode.sonNode) > 0:
            self.context.m_scene.adjustNode(self.context.m_activateNode, self.node, True)
            self.context.m_scene.adjustBranch()

        self.context.m_scene.setActivateNode(self.context.m_activateNode)

    def redo(self):
        self.node.parentNode = self.context.m_activateNode
        self.context.m_activateNode.sonNode.append(self.node)
        self.node.setPos(*self.context.m_pos)
        if len(self.context.m_activateNode.sonNode) > 1:
            self.context.m_scene.adjustNode(self.context.m_activateNode, self.node)
            self.context.m_scene.adjustBranch()

        self.context.m_scene.setActivateNode(self.node)

        self.context.m_scene.addItem(self.node)
        self.context.m_scene.NodeList.append(self.node)

        self.context.m_scene.addBranch(self.node.parentNode, self.node)

class RemoveNodeCommand(QUndoCommand):
    """remove node"""
    def __init__(self, context, *args, **kwargs):
        super(RemoveNodeCommand, self).__init__(*args, **kwargs)

        self.context = context

    
    def undo(self):  
        for node in self.context.m_nodeList:
            node.parentNode.sonNode.append(node)
            print(node.x, node.y)
            node.setPos(node.x, node.y)
            if len(node.parentNode.sonNode) > 1:
                self.context.m_scene.adjustNode(node.parentNode, node)
                self.context.m_scene.adjustBranch()

            self.context.m_scene.addItem(node)
            self.context.m_scene.NodeList.append(node)

            self.context.m_scene.addBranch(node.parentNode, node)

        self.context.m_scene.setActivateNode(self.context.m_activateNode)

    def redo(self):
        for node in self.context.m_nodeList[::-1]:
            node.parentNode.sonNode.remove(node)
            self.context.m_scene.NodeList.remove(node)

            self.context.m_scene.removeBranch(node)
            self.context.m_scene.removeItem(node)

            if len(node.parentNode.sonNode) > 0:
                self.context.m_scene.adjustNode(node.parentNode, node, True)
                self.context.m_scene.adjustBranch()

        self.context.m_scene.setActivateNode(self.context.m_activateNode.parentNode)


class MoveCommand(QUndoCommand):
    """move node"""
    def __init__(self, context, *args, **kwargs):
        super(MoveCommand, self).__init__(*args, **kwargs)
        self.context = context

    def undo(self):
        for node in self.context.m_nodeList:
            dx, dy = self.context.m_pos
            node.moveBy(-dx, -dy)
            node.x -= dx
            node.y -= dy
        self.context.m_scene.adjustBranch()
        self.context.m_scene.setActivateNode(self.context.m_activateNode)

    def redo(self):
        for node in self.context.m_nodeList:
            dx, dy = self.context.m_pos
            node.moveBy(dx, dy)
            node.x += dx
            node.y += dy
        self.context.m_scene.adjustBranch()
        self.context.m_scene.setActivateNode(self.context.m_activateNode)

    def mergeWith(self, command):
        """merge movecommand"""
        if command.id() != self.id():
            print('id diff')
            return False
        if self.context.m_activateNode != command.context.m_activateNode:
            print('activate node diff')
            return False
        '''if self.context.m_nodeList != command.context.m_activateNode:
            print('subTree diff')
            return False'''
        self.context.m_pos[0] += command.context.m_pos[0]
        self.context.m_pos[1] += command.context.m_pos[1]

        return True

    def id(self):
        return MoveCommandID


class NodeColorCommand(QUndoCommand):
    """Change Node Color"""
    def __init__(self, context, *args, **kwargs):
        super(NodeColorCommand, self).__init__(*args, **kwargs)
        self.context = context
        self.color = self.context.m_activateNode.m_color

    def undo(self):
        print('node color undo')
        self.context.m_activateNode.setColor(self.color)
        self.context.m_scene.setActivateNode(self.context.m_activateNode)

    def redo(self):
        self.context.m_activateNode.setColor(self.context.m_color)
        self.context.m_scene.setActivateNode(self.context.m_activateNode)


class TextColorCommand(QUndoCommand):
    """Change Text Color"""
    def __init__(self, context, *args, **kwargs):
        super(TextColorCommand, self).__init__(*args, **kwargs)
        self.context = context
        self.textColor = self.context.m_activateNode.m_textColor

    def undo(self):
        self.context.m_activateNode.setTextColor(self.textColor)
        self.context.m_scene.setActivateNode(self.context.m_activateNode)

    def redo(self):
        self.context.m_activateNode.setTextColor(self.context.m_textColor)
        self.context.m_scene.setActivateNode(self.context.m_activateNode)


# TODO: Cut, Copy, Paste Command
class CutCommand(QUndoCommand):
    def __init__(self, context, *args, **kwargs):
        super(CutCommand, self).__init__(*args, **kwargs)

    def undo(self):
        pass

    def redo(self):
        pass


class CopyCommand(QUndoCommand):
    def __init__(self, context, *args, **kwargs):
        super(CopyCommand, self).__init__(*args, **kwargs)

    def undo(self):
        pass

    def redo(self):
        pass


class PasteCommand(QUndoCommand):
    def __init__(self, context, *args, **kwargs):
        super(PasteCommand, self).__init__(*args, **kwargs)

    def undo(self):
        pass

    def redo(self):
        pass