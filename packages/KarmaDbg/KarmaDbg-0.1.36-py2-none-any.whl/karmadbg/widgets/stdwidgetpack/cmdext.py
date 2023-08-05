
from PySide.QtGui import QDockWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QFrame, QLineEdit, QTextCursor, QTextBrowser, QSplitter, QAction
from PySide.QtCore import Qt


from karmadbg.uicore.async import async

import cgi
import re
import pprint

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
        self.historyField.setLineWrapMode(QTextEdit.NoWrap)
        self.historyField.setOpenLinks(False)
        self.historyField.setHtml(self.htmlTemplate)
        self.historyField.anchorClicked.connect(self.onLinkClicked)
        self.historyField.document().setDefaultStyleSheet(uimanager.docCss)

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
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        self.setWidget(splitter)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

        self.uimanager.textOutputRequired.connect(self.onOutputRequired)
        self.uimanager.readyForCommand.connect(self.onCommandRequired)
        self.uimanager.textInputRequired.connect(self.onInputRequired)

        self.historyField.contextMenuEvent = self.contextMenuEvent
        self.inputField.keyPressEvent = self.onKeyPressEvent
        self.inputField.keyReleaseEvent = self.onKeyReleaseEvent
        self.inputField.insertFromMimeData = self.inputFieldInsertFromMime

    def onKeyPressEvent(self,event):  

        if event.key() == Qt.Key_Return and event.modifiers() == Qt.NoModifier:
            return 
        if event.key() == Qt.Key_Enter and event.modifiers() == Qt.NoModifier:
            return
        if event.key() == Qt.Key_Up:
            return
        if event.key() == Qt.Key_Down:
            return
        if event.key() == Qt.Key_Tab:
            return

        QTextEdit.keyPressEvent(self.inputField, event)


    def onKeyReleaseEvent(self, event):

        if event.key() == Qt.Key_Return:
            return self.onInputKeyRelease(event) if event.modifiers() == Qt.NoModifier else None

        if event.key() == Qt.Key_Enter:
            return self.onInputKeyRelease(event) if event.modifiers() == Qt.KeypadModifier else None

        if event.key() == Qt.Key_Up:
            return self.onKeyUpRelease(event)

        if event.key() == Qt.Key_Down:
            return self.onKeyDownRelease(event)

        if event.key() == Qt.Key_Tab:
            return self.onKeyTabRelease(event)

        QTextEdit.keyReleaseEvent(self.inputField, event)


    def contextMenuEvent(self, event):

        menu = self.historyField.createStandardContextMenu()
        menu.addSeparator()
        clearAction = QAction("Clear",self)
        clearAction.triggered.connect(lambda: self.historyField.setHtml(self.htmlTemplate))
        menu.addAction(clearAction)
        menu.popup(event.globalPos())

    def inputFieldInsertFromMime(self, mimeSource):
        QTextEdit.insertPlainText(self.inputField, mimeSource.text())

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

    @async
    def onKeyTabRelease(self,event):
        text = self.inputField.toPlainText()
        autoComplete = yield( self.uimanager.debugClient.getAutoCompleteAsync(text))

        if autoComplete:
            if autoComplete[0] == "filePath":
                self.autoCompleteFilePath(autoComplete)

    def autoCompleteFilePath(self, autoComplete):

        _, inputComplete, hints = autoComplete

        cursor = self.inputField.textCursor()
        cursor.movePosition(  QTextCursor.End, QTextCursor.MoveAnchor)
        cursor.insertText(inputComplete)

        if len(hints) > 1:
            hints = hints if  len(hints) < 40 else hints[:40]
            i = 0
            str = ""
            for hintType, hint in hints:
                if i % 4 == 0:
                    str += "<br>"
                if hintType == "file":
                    str += "&nbsp;&nbsp;&nbsp;&nbsp;<span class=\"filename\">"
                else:
                    str += "&nbsp;&nbsp;&nbsp;&nbsp;<span class=\"dirname\">"
                
                str += ("%- 20s</span>" % ( hint if len(hint) < 20 else hint[:20] )).replace(" ", "&nbsp;")
                i += 1
            str += "<br>"

            cursor = self.historyField.textCursor()
            cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
            cursor.insertHtml(str)
            cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
            self.historyField.ensureCursorVisible()


    def onLinkClicked(self, url):
        res = re.match("cmd:(.*)", url.toString())
        if res:
            self.uimanager.callCommand(res.group(1))
            return

        res = re.match("insert:(.*)", url.toString())
        if res:
            hint = res.group(1)
            cursor = self.inputField.textCursor()
            cursor.movePosition( QTextCursor.End, QTextCursor.MoveAnchor)
            cursor.insertText(hint)
        

    def onInputKeyRelease(self,event):
        self.inputField.setReadOnly(True)
        text = self.inputField.toPlainText()
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

        str = re.sub(r"<link cmd\s*=\s*\"", "<a href=\"cmd:", str)
        str = re.sub("</link>", "</a>", str)
        str = re.sub("<exec cmd", "<a href", str)
        str = re.sub("</exec>", "</a>", str)
        str = "<pre>" + str + "</pre>"

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
