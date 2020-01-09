# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
from Graph import Graph
from Component import *
from Config import *
        

class MainWindow(QMainWindow):
    """Main Window

    Show the main window for app

    Signals:
        addNote: (int, int, str) -> (pos_x, pos_y, note_text)
        addLink: (int, int, str) -> (pos_x, pos_y, link_text)
        close_signal: MainWindow close signal
    """
    addNote = pyqtSignal(int, int, str)
    addLink = pyqtSignal(int, int, str)
    close_signal = pyqtSignal()

    def __init__(self, settings):
        super().__init__()
        # self.path = None
        self.root = QFileInfo(__file__).absolutePath()
        self.m_contentChanged = False
        self.m_filename = None
        self.m_undoStack = None
        self.m_dockShow = True
        self.m_settings = settings
        self.timer = QTimer()
        self.timer.timeout.connect(self.file_autoSave)

        self.setWindowIcon(QIcon(self.root + '/images/window.jpg'))
        print(self.root)

        self.scene = Graph()
        self.scene.contentChanged.connect(self.contentChanged)
        self.scene.nodeNumChange.connect(self.nodeNumChange)
        self.scene.messageShow.connect(self.messageShow)

        self.view = QGraphicsView()
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        #view.setContextMenuPolicy(Qt.CustomContextMenu)
        # view.setInteractive(False)
        self.view.setScene(self.scene)

        self.setCentralWidget(self.view)
        self.view.show()

        self.initUI()

    def initUI(self):
        self.setUpDockWidget()
        self.setUpMenuBar()
        self.setUpToolBar()
        self.setUpStatusBar()
        self.setUpIconToolBar()

        self.update_title()

        self.resize(1200, 800)
        self.center()

        self.show()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def update_title(self):
        self.setWindowTitle('%s - MindMap' % (os.path.basename(self.m_filename) if self.m_filename else 'Untitled'))

    def setUpDockWidget(self):
        """Dock Widget Show Hot Key Help"""
        self.dock = QDockWidget('Hot Key Help', self)
        self.dock.setAllowedAreas(Qt.RightDockWidgetArea)
        hotkeyList = QListWidget(self)
        hotkeyList.addItems(['Ctrl + X 剪切', 'Ctrl + C 复制'])
        self.dock.setWidget(hotkeyList)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.hide()

    ###########################################################################
    #
    #  menubar
    #
    ###########################################################################
    def setUpMenuBar(self):
        self.m_undoStack = QUndoStack(self)
        #self.m_undoView = QUndoView(self.m_undoStack, self)
        ###########################################################################
        # file menu
        ###########################################################################
        file_menu = self.menuBar().addMenu('File')

        # new file
        new_file_action = QAction('New file', self)
        new_file_action.setShortcut('Ctrl+N')
        new_file_action.triggered.connect(self.file_new)
        file_menu.addAction(new_file_action)

        # open file
        open_file_action = QAction('Open file', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)

        # last open file
        self.last_open_file_menu = QMenu('Last open file', self)
        self.file_last_open()
        # TODO: function bind with action
        file_menu.addMenu(self.last_open_file_menu)

        file_menu.addSeparator()

        # save file
        self.save_file_action = QAction('Save', self)
        self.save_file_action.setShortcut('Ctrl+S')
        self.save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(self.save_file_action)

        # save file as ...
        saveas_file_action = QAction('Save as', self)
        saveas_file_action.setShortcut('Ctrl+Shift+S')
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)

        file_menu.addSeparator()

        # export as 
        exportas_menu = QMenu('Export as', self)
        # TODO: function bind with action
        exportas_png_action = QAction('PNG', self)
        exportas_png_action.triggered.connect(self.exportas_png)
        exportas_menu.addAction(exportas_png_action)

        exportas_pdf_action = QAction('PDF', self)
        exportas_pdf_action.triggered.connect(self.exportas_pdf)
        exportas_menu.addAction(exportas_pdf_action)

        file_menu.addMenu(exportas_menu)

        file_menu.addSeparator()

        # print file
        print_action = QAction('Print...', self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        # quit
        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.quit)
        file_menu.addAction(quit_action)

        #############################################################################
        # Edit menu
        #############################################################################
        edit_menu = self.menuBar().addMenu('Edit')

        # undo
        self.undo_action = self.m_undoStack.createUndoAction(self, 'Undo')
        self.undo_action.setShortcut('Ctrl+Z')
        edit_menu.addAction(self.undo_action)

        # Redo
        self.redo_action = self.m_undoStack.createRedoAction(self, 'Redo')
        self.redo_action.setShortcut('Ctrl+Y')
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        # Cut
        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.scene.cut)
        edit_menu.addAction(cut_action)

        # Copy
        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.scene.copy)
        edit_menu.addAction(copy_action)

        # Paste
        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.scene.paste)
        edit_menu.addAction(paste_action)

        # Delete
        delete_action = QAction('Delete', self)
        delete_action.setShortcut('Delete')
        delete_action.triggered.connect(self.scene.removeNode)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        ##########################################################################
        # Insert menu
        ##########################################################################
        insert_menu = self.menuBar().addMenu('Insert')

        add_notes_action = QAction('note', self)
        add_notes_action.triggered.connect(self.add_notes)
        insert_menu.addAction(add_notes_action)

        add_link_action = QAction('link', self)
        add_link_action.triggered.connect(self.add_link)
        insert_menu.addAction(add_link_action)

        add_icon_action = QAction('icon', self)
        add_icon_action.triggered.connect(self.add_icon)
        insert_menu.addAction(add_icon_action)

        ##########################################################################
        # Help menu
        ##########################################################################
        help_menu = self.menuBar().addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        hotKey_help_action = QAction('hot key help', self)
        hotKey_help_action.triggered.connect(self.hot_key)
        help_menu.addAction(hotKey_help_action)

    ###########################################################################
    #
    #  ToolBar
    #
    ############################################################################
    def setUpToolBar(self):
        self.toolbar = self.addToolBar('toolbar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        ###########################################################################
        #  New File
        ###########################################################################
        new_file_action = QAction(QIcon(self.root + '/images/filenew.png'), 'New File', self)
        new_file_action.triggered.connect(self.file_new)
        self.toolbar.addAction(new_file_action)

        ###########################################################################
        #  Save File
        ###########################################################################
        save_file_action = QAction(QIcon(self.root + '/images/filesave.png'), 'Save File', self)
        save_file_action.triggered.connect(self.file_save)
        self.toolbar.addAction(save_file_action)

        ###########################################################################
        #  Open File
        ###########################################################################
        open_file_action = QAction(QIcon(self.root + '/images/fileopen.png'), 'Open File', self)
        open_file_action.triggered.connect(self.file_open)
        self.toolbar.addAction(open_file_action)

        ###########################################################################
        #  New Sibling Node
        ###########################################################################
        new_siblingNode_action = QAction(QIcon(self.root + '/images/topicafter.svg'), 'topicafter', self)
        # new_node_action.setShortcut('Ctrl+N') 
        new_siblingNode_action.triggered.connect(self.scene.addSiblingNode)        
        self.toolbar.addAction(new_siblingNode_action)

        ############################################################################
        #  New Son Node
        ############################################################################
        new_sonNode_action = QAction(QIcon(self.root + '/images/subtopic.svg'), 'subtopic', self)
        new_sonNode_action.triggered.connect(self.scene.addSonNode)
        self.toolbar.addAction(new_sonNode_action)

        ############################################################################
        #  Add Branch
        ############################################################################
        add_branch_action = QAction(QIcon(self.root + '/images/relationship.svg'), 'relation', self)
        add_branch_action.triggered.connect(self.scene.buildRelation)
        self.toolbar.addAction(add_branch_action)

        ############################################################################
        #  Add Notes
        ############################################################################
        add_notes_action = QAction(QIcon(self.root + '/images/notes.svg'), 'note', self)
        add_notes_action.triggered.connect(self.add_notes)
        self.toolbar.addAction(add_notes_action)

        ############################################################################
        #  Delete
        ############################################################################
        addBranch_action = QAction(QIcon(self.root + '/images/delete.png'), 'Delete', self)
        addBranch_action.triggered.connect(self.scene.removeNode)
        self.toolbar.addAction(addBranch_action)

        ############################################################################
        #  undo
        #############################################################################
        self.undo_action.setIcon(QIcon(self.root + '/images/undo.png'))
        self.toolbar.addAction(self.undo_action)

        ##############################################################################
        #  redo
        ##############################################################################
        self.redo_action.setIcon(QIcon(self.root + '/images/redo.png'))
        self.toolbar.addAction(self.redo_action)

        self.scene.setUndoStack(self.m_undoStack)

    def setUpIconToolBar(self):
        self.icontoolbar = QToolBar('icon toolbar', self)

        m_signalMapper = QSignalMapper(self)

        # application-system
        application_system_action = QAction(QIcon(self.root + '/icons/applications-system.svg'), 'Applications-system', self)
        application_system_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(application_system_action, self.root + '/icons/applications-system.svg')

        # trash icon
        trash_action = QAction(QIcon(self.root + '/icons/user-trash-full.svg'), 'Trash', self)
        trash_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(trash_action, self.root + '/icons/user-trash-full.svg')

        # mail icon
        mail_action = QAction(QIcon(self.root + '/icons/mail-attachment.svg'), 'Mail', self)
        mail_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(mail_action, self.root + '/icons/mail-attachment.svg')

        # warn icon
        warn_action = QAction(QIcon(self.root + '/icons/dialog-warning.svg'), 'Warning', self)
        warn_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(warn_action, self.root + '/icons/dialog-warning.svg')

        # how icon
        help_action = QAction(QIcon(self.root + '/icons/help-browser.svg'), 'Help', self)
        help_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(help_action, self.root + '/icons/help-browser.svg')

        # calendar icon
        calendar_action = QAction(QIcon(self.root + '/icons/x-office-calendar.svg'), 'Calendar', self)
        calendar_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(calendar_action, self.root + '/icons/x-office-calendar.svg')

        # system_users icon
        system_users_action = QAction(QIcon(self.root + '/icons/system-users.svg'), 'System-users', self)
        system_users_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(system_users_action, self.root + '/icons/system-users.svg')

        # info icon
        info_action = QAction(QIcon(self.root + '/icons/dialog-information.svg'), 'Infomation', self)
        info_action.triggered.connect(m_signalMapper.map)
        m_signalMapper.setMapping(info_action, self.root + '/icons/dialog-information.svg')

        m_signalMapper.mapped[str].connect(self.scene.insertPicture)

        self.icontoolbar.addAction(application_system_action)
        self.icontoolbar.addAction(trash_action)
        self.icontoolbar.addAction(mail_action)
        self.icontoolbar.addAction(warn_action)
        self.icontoolbar.addAction(help_action)
        self.icontoolbar.addAction(calendar_action)
        self.icontoolbar.addAction(system_users_action)
        self.icontoolbar.addAction(info_action)

        self.addToolBar(Qt.LeftToolBarArea, self.icontoolbar)
        self.icontoolbar.hide()

    def setUpStatusBar(self):
        zoomSlider = MySlider(self.view, Qt.Horizontal)
        zoomSlider.setMaximumWidth(200)
        zoomSlider.setRange(1, 200)
        zoomSlider.setSingleStep(10)
        zoomSlider.setValue(100)

        self.label1 = QLabel('100%')
        self.label2 = QLabel('主题: 1')
        self.label3 = QLabel('welcome to 429 mindmap!')

        widget = QWidget(self)
        hbox = QHBoxLayout()
        
        hbox.addWidget(self.label2)
        hbox.addWidget(zoomSlider)
        hbox.addWidget(self.label1)
        hbox.addWidget(self.label3)

        widget.setLayout(hbox)

        zoomSlider.valueChanged.connect(self.labelShow)        

        self.statusBar().addWidget(widget, 5)
    
    def nodeNumChange(self, v):
        self.label2.setText('主题: ' + str(v))

    def labelShow(self, v):
        self.label1.setText(str(v) + '%')
    
    def messageShow(self, text):
        self.label3.setText(text)

    def contentChanged(self, changed=True):
        print(self.m_contentChanged)
        if not self.m_contentChanged and changed:
            self.timer.start(AUTOSAVE_TIME)
            self.setWindowTitle('*' + self.windowTitle())
            self.m_contentChanged = True

            fileinfo = QFileInfo(self.m_filename)
            if 'Untitled' not in self.windowTitle() and fileinfo.isWritable():
                self.save_file_action.setEnabled(True)
        
        elif self.m_contentChanged and not changed:
            self.timer.stop()
            self.setWindowTitle(self.windowTitle()[1:])
            self.m_contentChanged = False
            self.save_file_action.setEnabled(False)

    # TODO: scene center move
    def file_new(self):
        if not self.close_file():
            return

        self.m_filename = None
        self.scene.addFirstNode()
        self.update_title()
    
    # TODO: make sure file is valid !
    def file_open(self, filename=''):
        if not self.close_file():
            return

        cur_filename = self.m_filename
        if not filename:
            if self.sender().text() in self.m_settings.value('lastpath'):
                self.m_filename = self.root + '/files/' + self.sender().text()
                print(self.m_filename)
            else:
                dialog = QFileDialog(self, 'Open mindmap', self.root + '/files', 'MindMap(*.mm)')
                dialog.setAcceptMode(QFileDialog.AcceptOpen)
                dialog.setDefaultSuffix('mm')

                if not dialog.exec():
                    return
                self.m_filename = dialog.selectedFiles()[0]    
        else:
            self.m_filename = filename

        fileInfo = QFileInfo(self.m_filename)
        if not fileInfo.isWritable():
            print('Read-Only File !')
        
        if not self.scene.readContentFromXmlFile(self.m_filename):
            self.m_filename = cur_filename
            return

        lastpath = self.m_settings.value('lastpath')
        if os.path.basename(self.m_filename) not in lastpath:
            lastpath.append(os.path.basename(self.m_filename))
            self.m_settings.setValue('lastpath', lastpath)
            self.file_last_open()
        
        self.update_title()

    def file_last_open(self):
        lastpath = self.m_settings.value('lastpath')

        if not lastpath:
            last_open_action = QAction('no last file', self)
            self.last_open_file_menu.addAction(last_open_action)
        else:
            self.last_open_file_menu.clear()
            for filename in lastpath:
                last_open_action = QAction(filename, self)
                last_open_action.triggered.connect(self.file_open)
                self.last_open_file_menu.addAction(last_open_action)

    def file_save(self, checkIfReadOnly=True):
        fileinfo = QFileInfo(self.m_filename)
        if checkIfReadOnly and not fileinfo.isWritable():
            self.messageShow('Error: the file is read only !')
            return

        print(self.m_filename)
        self.scene.writeContentToXmlFile(self.m_filename)
        self.contentChanged(False)
        self.m_undoStack.clear()

    def file_autoSave(self):
        fileInfo = QFileInfo(self.m_filename)
        if self.windowTitle() != 'Untitled' and fileInfo.isWritable():
            self.file_save()

    def file_saveas(self):
        dialog = QFileDialog(self, 'Save mindmap as', self.root + '/files', 'MindMap(*.mm)')
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix('mm')

        if not dialog.exec():
            return False

        self.m_filename = dialog.selectedFiles()[0]
        print(dialog.selectedFiles())
        self.file_save(False)
        self.update_title()

    def file_print(self):
        printer = QPrinter(QPrinter.HighResolution)
        if QPrintDialog(printer).exec() == QDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()

    def close_file(self):
        if self.m_contentChanged:
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle('Save MindMap')
            msgBox.setText('The MindMap has been modified !')
            msgBox.setInformativeText('Do you want to save this file ?')
            msgBox.setStandardButtons(QMessageBox.Save|
                                        QMessageBox.Discard|
                                        QMessageBox.Cancel)

            msgBox.setDefaultButton(QMessageBox.Save)
            ret = msgBox.exec()

            if ret == QMessageBox.Save:
                if 'Untitled' in self.windowTitle():
                    if not self.file_saveas():
                        return False
                else:
                    self.file_save()
            elif ret == QMessageBox.Cancel:
                return False

        self.m_contentChanged = False
        self.scene.removeAllNodes()
        self.scene.removeAllBranches()
        self.m_undoStack.clear()
        return True

    def exportas_png(self):
        dialog = QFileDialog(self, 'Export mindmap as', self.root + '/files', 'MindMap(*.png)')
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix('png')

        if not dialog.exec():
            return False

        png_filename = dialog.selectedFiles()[0]
        print(dialog.selectedFiles())
        self.scene.writeContentToPngFile(png_filename)

    def exportas_pdf(self):
        dialog = QFileDialog(self, 'Export mindmap as', self.root + '/files', 'MindMap(*.pdf)')
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix('pdf')

        if not dialog.exec():
            return False

        pdf_filename = dialog.selectedFiles()[0]
        print(dialog.selectedFiles())
        self.scene.writeContentToPdfFile(pdf_filename)
            
    def quit(self):
        self.close_signal.emit()
        if self.m_contentChanged and not self.close_file():
            return
        qApp.quit()

    def closeEvent(self, e):
        self.close_signal.emit()
        if self.m_contentChanged and not self.close_file():
            e.ignore()
        else:
            e.accept()

    def getPos(self, size):
        p = QPointF(self.scene.m_activateNode.boundingRect().center().x(), 
                self.scene.m_activateNode.boundingRect().bottomRight().y())
        sceneP = self.scene.m_activateNode.mapToScene(p)
        viewP = self.view.mapFromScene(sceneP)
        pos = self.view.viewport().mapToGlobal(viewP)
        x = pos.x() - size[0]/2
        y = pos.y()
        return x, y

    def add_notes(self):
        x, y = self.getPos(NOTE_SIZE)
        print(x, y)
        self.addNote.emit(x, y, self.scene.m_activateNode.m_note)

    def getNote(self, note):
        self.scene.m_activateNode.m_note = note

    def add_link(self):
        x, y = self.getPos(LINK_SIZE)
        print(x, y)
        self.addLink.emit(x, y, self.scene.m_activateNode.m_link)

    def getLink(self, link):
        self.scene.m_activateNode.m_link = link
        if not self.scene.m_activateNode.hasLink and link != 'https://':
            self.scene.m_activateNode.hasLink = True
            self.scene.m_activateNode.insertLink(link)
            self.scene.adjustSubTreeNode()
            self.scene.adjustBranch()
        elif self.scene.m_activateNode.hasLink:
            self.scene.m_activateNode.updateLink(link)

    def about(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle('About 429 MindMap')
        msgBox.setText('MindMap written in PyQt5')
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setInformativeText('Report Bug to: \n 1140873504@qq.com')
        pic = QPixmap(self.root + '/images/window.jpg')
        msgBox.setIconPixmap(pic.scaled(50, 50))
        msgBox.exec()

    def hot_key(self):
        if not self.dock.isVisible():
            self.dock.show()

    def add_icon(self):
        if self.icontoolbar.isVisible():
            self.icontoolbar.hide()
        else:
            self.icontoolbar.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('MyXind')

    window = MainWindow()
    NoteWindow = Note()
    LinkWindow = Link()

    window.addNote.connect(NoteWindow.handle_addnote)
    window.close_signal.connect(NoteWindow.handle_close)
    window.scene.press_close.connect(NoteWindow.handle_close)

    NoteWindow.note.connect(window.getNote)
    NoteWindow.noteChange.connect(window.contentChanged)

    window.addLink.connect(LinkWindow.handle_addLink)
    window.close_signal.connect(LinkWindow.handle_close)
    window.scene.press_close.connect(LinkWindow.handle_close)

    LinkWindow.link.connect(window.getLink)
    LinkWindow.linkChange.connect(window.contentChanged)

    sys.exit(app.exec_())
