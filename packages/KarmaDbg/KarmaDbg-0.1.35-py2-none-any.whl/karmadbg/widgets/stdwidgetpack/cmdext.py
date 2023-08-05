
from PySide.QtGui import QDockWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QFrame, QLineEdit, QTextCursor, QTextBrowser, QSplitter
from PySide.QtCore import Qt

import cgi
import re

class CmdHtmlWidget( QDockWidget ):

    htmlTemplate = '''
<!DOCTYPE html>

<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <title></title>
</head>
<body>
</body>
</html>
    '''

    def __init__(self,widgetSettings, uimanager):
        super(CmdHtmlWidget,self).__init__()
        self.uimanager = uimanager

        self.historyCmd = []
        self.textInputRequired = False

        self.inputField =QTextEdit(self)
        self.inputField.setMinimumHeight(20)
        self.promptLabel = QLabel(">>>", self)
        self.historyField = QTextBrowser(self)
        self.historyField.setReadOnly(True)
        self.historyField.setOpenLinks(False)
        self.historyField.setHtml(self.htmlTemplate)
        self.historyField.anchorClicked.connect(self.onLinkClicked)

        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.promptLabel)
        vlayout.addStretch()
        hlayout.addLayout(vlayout)
        hlayout.addWidget(self.inputField)
        hlayout.setContentsMargins(0,0,4,4)
        frame = QFrame(self)
        frame.setMinimumHeight(20)
        frame.setLayout(hlayout)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.historyField)
        splitter.addWidget(frame)

        
        self.setWidget(splitter)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

        self.uimanager.textOutputRequired.connect(self.onOutputRequired)
        self.uimanager.readyForCommand.connect(self.onCommandRequired)
        self.uimanager.textInputRequired.connect(self.onInputRequired)

    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key_Return:
            return self.onInputKeyRelease(event) if event.modifiers() == Qt.NoModifier else None

        if event.key() == Qt.Key_Enter:
            return self.onInputKeyRelease(event) if event.modifiers() == Qt.KeypadModifier else None

        if event.key() == Qt.Key_Up:
            return self.onKeyUpRelease(event)

        if event.key() == Qt.Key_Down:
            return self.onKeyDownRelease(event)

        #if event.key() == Qt.Key_Tab:
        #    return self.onKeyTabRelease(event)

        super(CmdHtmlWidget, self).keyReleaseEvent(event)

    def onKeyUpRelease(self,event):
        self.historyForward()
        cursor = self.inputField.textCursor()
        cursor.setPosition( 0, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.End, QTextCursor.KeepAnchor )
        cursor.insertText(self.getHistory(0))

    def onKeyDownRelease(self,event):
        self.historyBack()
        cursor = self.inputField.textCursor()
        cursor.setPosition( 0, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.End, QTextCursor.KeepAnchor )
        cursor.insertText(self.getHistory(0))


    def onLinkClicked(self, url):
        self.uimanager.callCommand(url.toString())

    def onInputKeyRelease(self,event):
        self.inputField.setReadOnly(True)
        text = self.inputField.toPlainText()[:-1]
        self.inputField.setPlainText("")
        if self.textInputRequired == False:
            if text and ( len(self.historyCmd) == 0 or ( text != self.historyCmd[0] and text != self.historyCmd[-1] ) ):
                self.historyCmd.append(text)
                if len( self.historyCmd ) > 100:
                    self.historyCmd.pop()
            self.uimanager.callCommand(text)
        else:
            self.textInputRequired = False
            self.uimanager.textInputComplete(text)
        
    def onOutputRequired(self, str, dml):

        if not dml:
            str = cgi.escape(str)
       
        str = str.replace("\n", "<br>")

        str = re.sub("<link cmd", "<a href", str)
        str = re.sub("</link>", "</a>", str)
        str = re.sub("<exec cmd", "<a href", str)
        str = re.sub("</exec>", "</a>", str)
        
        cursor = self.historyField.textCursor()
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        cursor.insertHtml(str)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.historyField.ensureCursorVisible()

    def onCommandRequired(self):
        self.inputField.setReadOnly(False)

    def onInputRequired(self):
        self.inputField.setReadOnly(False)
        self.textInputRequired = True

    def historyForward(self):
        if len(self.historyCmd):
            cmd = self.historyCmd[-1]
            self.historyCmd.pop()
            self.historyCmd.insert( 0, cmd )

    def historyBack(self):
        if len(self.historyCmd):
            cmd = self.historyCmd[0]
            self.historyCmd.pop(0)
            self.historyCmd.append( cmd )

    def getHistory(self,index):
        return self.historyCmd[index] if index < len(self.historyCmd) else ""
