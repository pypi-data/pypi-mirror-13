# This file is part of ReText
# Copyright: 2012-2015 Dmitry Shachnev
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from markups import MarkdownMarkup
from ReText import globalSettings, tablemode, readFromSettings

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QKeyEvent, QPainter, QPalette, QTextCursor, QTextFormat
from PyQt5.QtWidgets import QLabel, QTextEdit, QWidget

colors = {
	'marginLine': QColor(0xdc, 0xd2, 0xdc),
	'currentLineHighlight': QColor(0xff, 0xff, 0xc8),
	'infoArea': QColor(0xaa, 0xff, 0x55, 0xaa),
	'lineNumberArea': Qt.cyan,
	'lineNumberAreaText': Qt.darkCyan
}

colorValues = {
	colorName: readFromSettings(
		'ColorScheme/' + colorName, QColor, default=colors[colorName])
	for colorName in colors
}

def documentIndentMore(document, cursor, globalSettings=globalSettings):
	if cursor.hasSelection():
		block = document.findBlock(cursor.selectionStart())
		end = document.findBlock(cursor.selectionEnd()).next()
		cursor.beginEditBlock()
		while block != end:
			cursor.setPosition(block.position())
			if globalSettings.tabInsertsSpaces:
				cursor.insertText(' ' * globalSettings.tabWidth)
			else:
				cursor.insertText('\t')
			block = block.next()
		cursor.endEditBlock()
	else:
		indent = globalSettings.tabWidth - (cursor.positionInBlock()
			% globalSettings.tabWidth)
		if globalSettings.tabInsertsSpaces:
			cursor.insertText(' ' * indent)
		else:
			cursor.insertText('\t')

def documentIndentLess(document, cursor, globalSettings=globalSettings):
	if cursor.hasSelection():
		block = document.findBlock(cursor.selectionStart())
		end = document.findBlock(cursor.selectionEnd()).next()
	else:
		block = document.findBlock(cursor.position())
		end = block.next()
	cursor.beginEditBlock()
	while block != end:
		cursor.setPosition(block.position())
		if document.characterAt(cursor.position()) == '\t':
			cursor.deleteChar()
		else:
			pos = 0
			while document.characterAt(cursor.position()) == ' ' \
			and pos < globalSettings.tabWidth:
				pos += 1
				cursor.deleteChar()
		block = block.next()
	cursor.endEditBlock()

class ReTextEdit(QTextEdit):
	def __init__(self, parent):
		QTextEdit.__init__(self)
		self.tab = parent
		self.parent = parent.p
		self.undoRedoActive = False
		self.tableModeEnabled = False
		self.setAcceptRichText(False)
		self.lineNumberArea = LineNumberArea(self)
		self.infoArea = InfoArea(self)
		self.updateFont()
		self.document().blockCountChanged.connect(self.updateLineNumberAreaWidth)
		self.cursorPositionChanged.connect(self.highlightCurrentLine)
		self.document().contentsChange.connect(self.contentsChange)

	def updateFont(self):
		self.setFont(globalSettings.editorFont)
		metrics = self.fontMetrics()
		self.marginx = (self.document().documentMargin()
			+ metrics.width(' ' * globalSettings.rightMargin))
		self.setTabStopWidth(globalSettings.tabWidth * self.fontMetrics().width(' '))
		self.updateLineNumberAreaWidth()
		self.infoArea.updateTextAndGeometry()

	def paintEvent(self, event):
		if not globalSettings.rightMargin:
			return QTextEdit.paintEvent(self, event)
		painter = QPainter(self.viewport())
		painter.setPen(colorValues['marginLine'])
		y1 = self.rect().topLeft().y()
		y2 = self.rect().bottomLeft().y()
		painter.drawLine(self.marginx, y1, self.marginx, y2)
		QTextEdit.paintEvent(self, event)

	def scrollContentsBy(self, dx, dy):
		QTextEdit.scrollContentsBy(self, dx, dy)
		self.lineNumberArea.update()

	def lineNumberAreaPaintEvent(self, event):
		painter = QPainter(self.lineNumberArea)
		painter.fillRect(event.rect(), colorValues['lineNumberArea'])
		cursor = QTextCursor(self.document())
		cursor.movePosition(QTextCursor.Start)
		atEnd = False
		while not atEnd:
			rect = self.cursorRect(cursor)
			block = cursor.block()
			if block.isVisible():
				number = str(cursor.blockNumber() + 1)
				painter.setPen(colorValues['lineNumberAreaText'])
				painter.drawText(0, rect.top(), self.lineNumberArea.width()-2,
					self.fontMetrics().height(), Qt.AlignRight, number)
			cursor.movePosition(QTextCursor.EndOfBlock)
			atEnd = cursor.atEnd()
			if not atEnd:
				cursor.movePosition(QTextCursor.NextBlock)

	def contextMenuEvent(self, event):
		text = self.toPlainText()
		dictionary = self.tab.highlighter.dictionary
		if (dictionary is None) or not text:
			return QTextEdit.contextMenuEvent(self, event)
		oldcursor = self.textCursor()
		cursor = self.cursorForPosition(event.pos())
		pos = cursor.positionInBlock()
		if pos == len(text): pos -= 1
		curchar = text[pos]
		isalpha = curchar.isalpha()
		cursor.select(QTextCursor.WordUnderCursor)
		if not isalpha or (oldcursor.hasSelection() and
		oldcursor.selectedText() != cursor.selectedText()):
			return QTextEdit.contextMenuEvent(self, event)
		self.setTextCursor(cursor)
		word = cursor.selectedText()
		if not word or dictionary.check(word):
			self.setTextCursor(oldcursor)
			return QTextEdit.contextMenuEvent(self, event)
		suggestions = dictionary.suggest(word)
		actions = [self.parent.act(sug, trig=self.fixWord(sug)) for sug in suggestions]
		menu = self.createStandardContextMenu()
		menu.insertSeparator(menu.actions()[0])
		for action in actions[::-1]:
			menu.insertAction(menu.actions()[0], action)
		menu.exec(event.globalPos())

	def fixWord(self, correctword):
		return lambda: self.insertPlainText(correctword)

	def keyPressEvent(self, event):
		key = event.key()
		cursor = self.textCursor()
		if event.text() and self.tableModeEnabled:
			cursor.beginEditBlock()
		if key == Qt.Key_Backspace and event.modifiers() & Qt.GroupSwitchModifier:
			# Workaround for https://bugreports.qt.io/browse/QTBUG-49771
			event = QKeyEvent(event.type(), event.key(),
				event.modifiers() ^ Qt.GroupSwitchModifier)
		if key == Qt.Key_Tab:
			documentIndentMore(self.document(), cursor)
		elif key == Qt.Key_Backtab:
			documentIndentLess(self.document(), cursor)
		elif key == Qt.Key_Return and not cursor.hasSelection():
			if event.modifiers() & Qt.ShiftModifier:
				# Insert Markdown-style line break
				markupClass = self.tab.getMarkupClass()
				if markupClass and markupClass == MarkdownMarkup:
					cursor.insertText('  ')
			if event.modifiers() & Qt.ControlModifier:
				cursor.insertText('\n')
			else:
				self.handleReturn(cursor)
		else:
			QTextEdit.keyPressEvent(self, event)
		if event.text() and self.tableModeEnabled:
			cursor.endEditBlock()

	def handleReturn(self, cursor):
		# Select text between the cursor and the line start
		cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
		text = cursor.selectedText()
		length = len(text)
		pos = 0
		while pos < length and (text[pos] in (' ', '\t')
		  or text[pos:pos+2] in ('* ', '- ')):
			pos += 1
		# Reset the cursor
		cursor = self.textCursor()
		cursor.insertText('\n'+text[:pos])
		self.ensureCursorVisible()

	def lineNumberAreaWidth(self):
		if not globalSettings.lineNumbersEnabled:
			return 0
		cursor = QTextCursor(self.document())
		cursor.movePosition(QTextCursor.End)
		digits = len(str(cursor.blockNumber() + 1))
		return 5 + self.fontMetrics().width('9') * digits

	def updateLineNumberAreaWidth(self, blockcount=0):
		self.lineNumberArea.update()
		self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

	def resizeEvent(self, event):
		QTextEdit.resizeEvent(self, event)
		rect = self.contentsRect()
		self.lineNumberArea.setGeometry(rect.left(), rect.top(),
			self.lineNumberAreaWidth(), rect.height())
		self.infoArea.updateTextAndGeometry()

	def highlightCurrentLine(self):
		if not globalSettings.highlightCurrentLine:
			return self.setExtraSelections([])
		selection = QTextEdit.ExtraSelection();
		selection.format.setBackground(colorValues['currentLineHighlight'])
		selection.format.setProperty(QTextFormat.FullWidthSelection, True)
		selection.cursor = self.textCursor()
		selection.cursor.clearSelection()
		self.setExtraSelections([selection])

	def enableTableMode(self, enable):
		self.tableModeEnabled = enable

	def backupCursorPositionOnLine(self):
		return self.textCursor().positionInBlock()

	def restoreCursorPositionOnLine(self, positionOnLine):
		cursor = self.textCursor()
		cursor.setPosition(cursor.block().position() + positionOnLine)
		self.setTextCursor(cursor)

	def contentsChange(self, pos, removed, added):
		if self.tableModeEnabled:
			markupClass = self.tab.getMarkupClass()

			cursorPosition = self.backupCursorPositionOnLine()
			tablemode.adjustTableToChanges(self.document(), pos, added - removed, markupClass)
			self.restoreCursorPositionOnLine(cursorPosition)

class LineNumberArea(QWidget):
	def __init__(self, editor):
		QWidget.__init__(self, editor)
		self.editor = editor

	def sizeHint(self):
		return QSize(self.editor.lineNumberAreaWidth(), 0)

	def paintEvent(self, event):
		if globalSettings.lineNumbersEnabled:
			return self.editor.lineNumberAreaPaintEvent(event)

class InfoArea(QLabel):
	def __init__(self, editor):
		QWidget.__init__(self, editor)
		self.editor = editor
		self.editor.cursorPositionChanged.connect(self.updateTextAndGeometry)
		self.updateTextAndGeometry()
		self.setAutoFillBackground(True)
		palette = self.palette()
		palette.setColor(QPalette.Window, colorValues['infoArea'])
		self.setPalette(palette)

	def updateTextAndGeometry(self):
		text = self.getText()
		self.setText(text)
		viewport = self.editor.viewport()
		metrics = self.fontMetrics()
		width = metrics.width(text)
		height = metrics.height()
		self.resize(width, height)
		rightSide = viewport.width() + self.editor.lineNumberAreaWidth()
		self.move(rightSide - width, viewport.height() - height)
		self.setVisible(not globalSettings.useFakeVim)

	def getText(self):
		template = '%d : %d'
		cursor = self.editor.textCursor()
		block = cursor.blockNumber() + 1
		position = cursor.positionInBlock()
		return template % (block, position)
