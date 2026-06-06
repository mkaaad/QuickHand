import os
import sys
import sqlite3

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from PIL import Image, ImageFont
from handright import Template, handwrite, LayoutError

from moduels.GenerateImagesThread import GenerateImagesThread
from moduels.ColorLabel import ColorLabel
# 参考 https://github.com/Gsllchb/Handright/blob/master/docs/tutorial.md

class HandRightTab(QWidget):
    def __init__(self, parent, conn, presetTableName, preferenceTableName='preference'):
        super(HandRightTab, self).__init__(parent)
        self.conn = conn
        self.presetTableName = presetTableName
        self.preferenceTableName = preferenceTableName
        self.initGui()
        self.refreshList()
        self.connectSlots()
        self.initValue()

    def initGui(self):

        self.inputBox = QPlainTextEdit()
        self.charCountLabel = QLabel('字数：0')
        self.charCountLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.outputPathHint = QLabel('输出路径')
        self.outputPathBox = QLineEdit()
        self.outputBrowseBtn = QPushButton('浏览')
        self.outputOpenBtn = QPushButton('打开输出文件夹')

        self.runBtn = QPushButton('运行')
        self.previewBtn = QPushButton('预览')
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setFormat('')
        self.progressBar.hide()
        self.logBox = QPlainTextEdit()
        self.logBox.setReadOnly(True)
        self.logBox.setMaximumBlockCount(1000)
        self.logBox.hide()

        self.backgroundBlankRadioBtn = QRadioButton('使用空白背景')
        self.backgroundImageRadioBtn = QRadioButton('使用背景图片')


        self.backgroundHint = QLabel('背景图片')
        self.backgroundBox = QComboBox()
        self.backgroundBrowseBtn = QPushButton('浏览')

        self.backgroundSizeHint = QLabel('背景图片大小')
        self.backgroundSizeBoxX = QLineEdit()
        self.backgroundSizeBoxMultipleHint = QLabel('×')
        self.backgroundSizeBoxY = QLineEdit()


        self.fontPathHint = QLabel('字体')
        self.fontPathBox = QComboBox()

        self.fontSizeHint = QLabel('字体大小')
        self.fontSizeBox = QSpinBox()

        self.fontColorHint = QLabel('字体颜色')
        self.fontColorBox = ColorLabel('')

        self.lineSpacingHint = QLabel('行间距')
        self.lineSpacingBox = QSpinBox()

        self.wordSpacingHint = QLabel('字符间距')
        self.wordSpacingBox = QSpinBox()



        self.leftMarginHint = QLabel('页面左边距')
        self.leftMarginBox = QSpinBox()

        self.topMarginHint = QLabel('页面上边距')
        self.topMarginBox = QSpinBox()

        self.rightMarginHint = QLabel('页面右边距')
        self.rightMarginBox = QSpinBox()

        self.bottomMarginHint = QLabel('页面下边距')
        self.bottomMarginBox = QSpinBox()



        self.lindSpacingSigmaHint = QLabel('行间距扰动')
        self.lindSpacingSigmaBox = QSpinBox()

        self.fontSizeSigmaHint = QLabel('字体大小扰动')
        self.fontSizeSigmaBox = QSpinBox()

        self.wordSpacingSigmaHint = QLabel('字间距扰动')
        self.wordSpacingSigmaBox = QSpinBox()

        self.perturbXSigmaHint = QLabel('笔画横向偏移扰动')
        self.perturbXSigmaBox = QSpinBox()

        self.perturbYSigmaHint = QLabel('笔画纵向偏移扰动')
        self.perturbYSigmaBox = QSpinBox()

        self.perturbThetaSigmaHint = QLabel('笔画旋转偏移扰动')
        self.perturbThetaSigmaBox = QDoubleSpinBox()

        self.endCharsHint = QLabel('防止行首字符')
        self.endCharsBox = QLineEdit()

        self.showImageBox = QCheckBox('每生成一张图片后自动打开')

        self.outputFormatHint = QLabel('输出格式')
        self.outputFormatBox = QComboBox()

        self.hideToSystemTraySwitch = QCheckBox('点击关闭按钮时隐藏到托盘')

        self.presetHint = QLabel('预设列表')
        self.presetList = QListWidget()

        self.upPresetBtn = QPushButton('↑')
        self.downPresetBtn = QPushButton('↓')
        self.addPresetBtn = QPushButton('+')
        self.delPresetBtn = QPushButton('-')


        self.outputLayout = QHBoxLayout()
        self.outputLayout.setContentsMargins(0,0,0,0)
        self.outputLayout.addWidget(self.outputPathHint)
        self.outputLayout.addWidget(self.outputPathBox)
        self.outputLayout.addWidget(self.outputBrowseBtn)
        self.outputLayout.addWidget(self.outputOpenBtn)
        self.outputBox = QWidget()
        self.outputBox.setContentsMargins(0,0,0,0)
        self.outputBox.setLayout(self.outputLayout)
        self.inputAndRunLayout = QVBoxLayout()
        self.inputAndRunLayout.addWidget(self.inputBox)
        self.inputAndRunLayout.addWidget(self.charCountLabel)
        self.inputAndRunLayout.addWidget(self.outputBox)
        self.inputAndRunLayout.addWidget(self.progressBar)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.runBtn)
        btnLayout.addWidget(self.previewBtn)
        self.inputAndRunLayout.addLayout(btnLayout)
        self.inputAndRunLayout.addWidget(self.logBox)
        self.inputAndRunBox = QWidget()
        self.inputAndRunBox.setLayout(self.inputAndRunLayout)




        self.backgroundTypeLayout = QHBoxLayout()  # 关于背景类型的两个按钮放置的布局
        self.backgroundTypeLayout.addWidget(self.backgroundBlankRadioBtn)
        self.backgroundTypeLayout.addWidget(self.backgroundImageRadioBtn)
        self.backgroundTypeBox = QWidget()
        self.backgroundTypeBox.setContentsMargins(0,0,0,0)
        self.backgroundTypeBox.setLayout(self.backgroundTypeLayout)

        self.backgroundSizeLayout = QHBoxLayout()  # 关于背景大小
        self.backgroundSizeLayout.setContentsMargins(0,0,0,0)
        self.backgroundSizeLayout.addWidget(self.backgroundSizeBoxX)
        self.backgroundSizeLayout.addWidget(self.backgroundSizeBoxMultipleHint)
        self.backgroundSizeLayout.addWidget(self.backgroundSizeBoxY)
        self.backgroundSizeBox = QWidget()
        self.backgroundSizeBox.setContentsMargins(0, 0, 0, 0)
        self.backgroundSizeBox.setLayout(self.backgroundSizeLayout)

        self.optionsLayout = QFormLayout()
        self.optionsLayout.setWidget(0, QFormLayout.SpanningRole, self.backgroundTypeBox) # 背景类型
        self.backgroundSelectLayout = QHBoxLayout()
        self.backgroundSelectLayout.setContentsMargins(0,0,0,0)
        self.backgroundSelectLayout.addWidget(self.backgroundBox)
        self.backgroundSelectLayout.addWidget(self.backgroundBrowseBtn)
        self.backgroundSelectBox = QWidget()
        self.backgroundSelectBox.setContentsMargins(0,0,0,0)
        self.backgroundSelectBox.setLayout(self.backgroundSelectLayout)
        self.optionsLayout.addRow(self.backgroundHint, self.backgroundSelectBox)  # 背景图片
        self.optionsLayout.setWidget(2, QFormLayout.LabelRole, self.backgroundSizeHint) # 背景大小
        self.optionsLayout.setWidget(2, QFormLayout.FieldRole, self.backgroundSizeBox) # 背景大小
        self.optionsLayout.addRow(QLabel(''), QLabel(''))  # 空白行
        self.optionsLayout.addRow(self.fontPathHint, self.fontPathBox)  # 字体
        self.optionsLayout.addRow(self.fontSizeHint, self.fontSizeBox)  # 字体大小
        self.optionsLayout.addRow(self.fontColorHint, self.fontColorBox)  # 字体颜色
        self.optionsLayout.addRow(self.lineSpacingHint, self.lineSpacingBox)  # 行间距
        self.optionsLayout.addRow(self.wordSpacingHint, self.wordSpacingBox)  # 字符间距
        self.optionsLayout.addRow(QLabel(''), QLabel(''))  # 空白行
        self.optionsLayout.addRow(self.leftMarginHint, self.leftMarginBox)  # 左边距
        self.optionsLayout.addRow(self.topMarginHint, self.topMarginBox)  # 上边距
        self.optionsLayout.addRow(self.rightMarginHint, self.rightMarginBox)  # 右边距
        self.optionsLayout.addRow(self.bottomMarginHint, self.bottomMarginBox)  # 下边距
        self.optionsLayout.addRow(QLabel(''), QLabel(''))  # 空白行
        self.optionsLayout.addRow(self.lindSpacingSigmaHint, self.lindSpacingSigmaBox)  # 行间距扰动
        self.optionsLayout.addRow(self.fontSizeSigmaHint, self.fontSizeSigmaBox)  # 字体大小扰动
        self.optionsLayout.addRow(self.wordSpacingSigmaHint, self.wordSpacingSigmaBox)  # 字间距扰动
        self.optionsLayout.addRow(self.perturbXSigmaHint, self.perturbXSigmaBox)  # 笔画横向偏移扰动
        self.optionsLayout.addRow(self.perturbYSigmaHint, self.perturbYSigmaBox)  # 行间距扰动
        self.optionsLayout.addRow(self.perturbThetaSigmaHint, self.perturbThetaSigmaBox)  # 行间距扰动
        self.optionsLayout.addRow(self.endCharsHint, self.endCharsBox)  # 防止行首字符
        self.optionsLayout.addRow(QLabel(''), QLabel(''))  # 空白行
        self.optionsLayout.setWidget(23, QFormLayout.SpanningRole, self.showImageBox)
        self.optionsLayout.addRow(self.outputFormatHint, self.outputFormatBox)  # 输出格式
        self.optionsLayout.addRow(QLabel(''), self.hideToSystemTraySwitch)


        self.optionsBox = QWidget()
        self.optionsBox.setLayout(self.optionsLayout)


        self.presetLayout = QGridLayout()
        self.presetLayout.addWidget(self.presetHint, 0,0,1,2)
        self.presetLayout.addWidget(self.presetList, 1,0,1,2)
        self.presetLayout.addWidget(self.upPresetBtn, 2,0,1,1)
        self.presetLayout.addWidget(self.downPresetBtn, 2,1,1,1)
        self.presetLayout.addWidget(self.addPresetBtn, 3,0,1,1)
        self.presetLayout.addWidget(self.delPresetBtn, 3,1,1,1)
        self.presetBox = QWidget()
        self.presetBox.setLayout(self.presetLayout)



        self.splitBetweenOptionAndPesetTable = QSplitter()
        self.splitBetweenOptionAndPesetTable.addWidget(self.optionsBox)
        self.splitBetweenOptionAndPesetTable.addWidget(self.presetBox)

        self.splitBetweenInputAndOption = QSplitter()
        self.splitBetweenInputAndOption.addWidget(self.inputAndRunBox)
        self.splitBetweenInputAndOption.addWidget(self.splitBetweenOptionAndPesetTable)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.addWidget(self.splitBetweenInputAndOption)

        self.setLayout(self.masterLayout)

    def initValue(self):
        font = QFont()
        font.setPointSize(12)
        self.inputBox.setFont(font)
        self.inputBox.setPlaceholderText('在这里输入要生成图片的文字')

        self.outputPathBox.setText(os.getcwd().replace('\\', '/') + '/output')

        self.backgroundBlankRadioBtn.click() # 启用或停用背景图片
        # self.switchUseable()

        self.backgroundBox.clear()
        self.backgroundBox.addItems(os.listdir('./backgrounds')) # 添加背景图片列表

        self.backgroundSizeBoxX.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter) # 初始化背景图片大小
        self.backgroundSizeBoxX.setValidator(QIntValidator(self))
        self.backgroundSizeBoxX.setText('2000')

        self.backgroundSizeBoxY.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter) # 初始化背景图片大小
        self.backgroundSizeBoxY.setValidator(QIntValidator(self))
        self.backgroundSizeBoxY.setText('2000')


        self.fontPathBox.clear()
        self.fontPathBox.addItems(os.listdir('./fonts')) # 添加字体列表

        self.outputFormatBox.addItems(['webp', 'png', 'jpg', 'bmp', 'tiff'])

        self.fontSizeBox.setSingleStep(5)
        self.fontSizeBox.setMinimum(1)
        self.fontSizeBox.setMaximum(2000)
        self.fontSizeBox.setValue(100)  # 设定字体初始大小
        self.fontSizeBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.lineSpacingBox.setSingleStep(10)
        self.lineSpacingBox.setMinimum(1)
        self.lineSpacingBox.setMaximum(2000)
        self.lineSpacingBox.setValue(120)  # 初始化行间距
        self.lineSpacingBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.wordSpacingBox.setSingleStep(5)
        self.wordSpacingBox.setMinimum(-1000)
        self.wordSpacingBox.setMaximum(2000)
        self.wordSpacingBox.setValue(120)  # 初始化字符间距
        self.wordSpacingBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.leftMarginBox.setSingleStep(5)
        self.leftMarginBox.setMinimum(1)
        self.leftMarginBox.setMaximum(2000)
        self.leftMarginBox.setValue(200)  # 初始化页面左边距
        self.leftMarginBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.topMarginBox.setSingleStep(5)
        self.topMarginBox.setMinimum(1)
        self.topMarginBox.setMaximum(2000)
        self.topMarginBox.setValue(200)  # 初始化页面上边距
        self.topMarginBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.rightMarginBox.setSingleStep(5)
        self.rightMarginBox.setMinimum(1)
        self.rightMarginBox.setMaximum(2000)
        self.rightMarginBox.setValue(200)  # 初始化页面右边剧
        self.rightMarginBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.bottomMarginBox.setSingleStep(5)
        self.bottomMarginBox.setMinimum(1)
        self.bottomMarginBox.setMaximum(2000)
        self.bottomMarginBox.setValue(200)  # 初始化页面下边距
        self.bottomMarginBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.lindSpacingSigmaBox.setSingleStep(1)
        self.lindSpacingSigmaBox.setMinimum(1)
        self.lindSpacingSigmaBox.setMaximum(1000)
        self.lindSpacingSigmaBox.setValue(6)  # 初始化行间距扰动
        self.lindSpacingSigmaBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.fontSizeSigmaBox.setSingleStep(2)
        self.fontSizeSigmaBox.setMinimum(1)
        self.fontSizeSigmaBox.setMaximum(1000)
        self.fontSizeSigmaBox.setValue(20)  # 初始化字体大小扰动
        self.fontSizeSigmaBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.wordSpacingSigmaBox.setSingleStep(1)
        self.wordSpacingSigmaBox.setMinimum(1)
        self.wordSpacingSigmaBox.setMaximum(1000)
        self.wordSpacingSigmaBox.setValue(3)  # 初始化字间距扰动
        self.wordSpacingSigmaBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.perturbXSigmaBox.setSingleStep(1)
        self.perturbXSigmaBox.setMinimum(1)
        self.perturbXSigmaBox.setMaximum(1000)
        self.perturbXSigmaBox.setValue(4)  # 笔画横向偏移扰动
        self.perturbXSigmaBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.perturbYSigmaBox.setSingleStep(1)
        self.perturbYSigmaBox.setMinimum(1)
        self.perturbYSigmaBox.setMaximum(1000)
        self.perturbYSigmaBox.setValue(4)  # 笔画纵向偏移扰动
        self.perturbYSigmaBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.perturbThetaSigmaBox.setSingleStep(1)
        self.perturbThetaSigmaBox.setDecimals(2)
        self.perturbThetaSigmaBox.setMinimum(0.00)
        self.perturbThetaSigmaBox.setMaximum(1)
        self.perturbThetaSigmaBox.setValue(0.05)  # 笔画旋转偏移扰动
        self.perturbThetaSigmaBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.endCharsBox.setText('，。！？')  # 防止行首字符
        self.endCharsBox.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)


        self.splitBetweenInputAndOption.setStretchFactor(0,5)
        self.splitBetweenInputAndOption.setStretchFactor(1,1)

        self.loadHideToTrayPreference()

    def connectSlots(self):
        self.runBtn.clicked.connect(self.run)
        self.previewBtn.clicked.connect(self.preview)
        self.inputBox.textChanged.connect(self.updateCharCount)
        self.backgroundBlankRadioBtn.clicked.connect(self.backgroundBlankRadioBtnClicked)
        self.backgroundImageRadioBtn.clicked.connect(self.backgroundImageRadioBtnClicked)
        self.upPresetBtn.clicked.connect(self.upMovePreset)
        self.downPresetBtn.clicked.connect(self.downMovePreset)
        self.addPresetBtn.clicked.connect(self.addPreset)
        self.delPresetBtn.clicked.connect(self.delPreset)
        self.presetList.itemClicked.connect(self.presetItemSelected)
        self.outputBrowseBtn.clicked.connect(self.browseOutputPath)
        self.outputOpenBtn.clicked.connect(self.openOutputPath)
        self.backgroundBrowseBtn.clicked.connect(self.browseBackground)
        self.hideToSystemTraySwitch.clicked.connect(self.hideToSystemTraySwitchClicked)


    def backgroundBlankRadioBtnClicked(self):
        self.useBackgroundImage = False
        self.backgroundHint.setEnabled(False)
        self.backgroundBox.setEnabled(False)
        self.backgroundBrowseBtn.setEnabled(False)
        self.backgroundSizeHint.setText('背景图片大小')
        self.backgroundSizeBoxX.setText('2000')
        self.backgroundSizeBoxY.setText('4000')

    def backgroundImageRadioBtnClicked(self):
        self.useBackgroundImage = True
        self.backgroundHint.setEnabled(True)
        self.backgroundBox.setEnabled(True)
        self.backgroundBrowseBtn.setEnabled(True)
        self.backgroundSizeHint.setText('背景图片缩放')
        self.backgroundSizeBoxX.setText('1')
        self.backgroundSizeBoxY.setText('1')

    def refreshList(self):
        cursor = self.conn.cursor()
        try:
            result = cursor.execute('''select name from %s order by id asc''' % (self.presetTableName)).fetchall()
        except:
            print('数据库读取不正常') # 这里可能还需要加一个重新载入数据库的操作, 不过懒得写了
        self.presetList.clear()
        for item in result:
            self.presetList.addItem(item[0])

    def presetItemSelected(self):
        currentRow = self.presetList.currentRow()
        currentItemName = self.presetList.item(currentRow).text()
        presetData = self.conn.cursor().execute('''select 
                                                        useBackgroundImage, imageName, 
                                                        backgroundSizeBoxX, backgroundSizeBoxY, fontName, fontSize, 
                                                        fontColor, lineSpacing, leftMargin, topMargin, 
                                                        rightMargin, bottomMargin, wordSpacing, lineSpacingSigma, 
                                                        fontSizeSigma, wordSpacingSigma, endChars, perturbXSigma, 
                                                        perturbYSigma, perturbThetaSigma
                                                    from %s where name = '%s'; ''' % (
                                                        self.presetTableName, currentItemName)).fetchone()

        useBackgroundImage = presetData[0]
        imageName = presetData[1]
        backgroundSizeBoxX = presetData[2]
        backgroundSizeBoxY = presetData[3]
        fontName = presetData[4]
        fontSize = presetData[5]
        fontColor = presetData[6]
        lineSpacing = presetData[7]
        leftMargin = presetData[8]
        topMargin = presetData[9]
        rightMargin = presetData[10]
        bottomMargin = presetData[11]
        wordSpacing = presetData[12]
        lineSpacingSigma = presetData[13]
        fontSizeSigma = presetData[14]
        wordSpacingSigma = presetData[15]
        endChars = presetData[16]
        perturbXSigma = presetData[17]
        perturbYSigma = presetData[18]
        perturbThetaSigma = presetData[19]

        if useBackgroundImage:
            self.backgroundImageRadioBtn.click()
        else:
            self.backgroundBlankRadioBtn.click()
        self.backgroundBox.setCurrentText(imageName)
        self.backgroundSizeBoxX.setText(str(backgroundSizeBoxX))
        self.backgroundSizeBoxY.setText(str(backgroundSizeBoxY))
        self.fontPathBox.setCurrentText(fontName)
        self.fontSizeBox.setValue(fontSize)
        colorTuple = tuple(eval(fontColor))
        print(colorTuple)
        self.fontColorBox.color = QColor()
        self.fontColorBox.color.setRgb(colorTuple[0], colorTuple[1], colorTuple[2])
        self.fontColorBox.setColor()
        self.lineSpacingBox.setValue(lineSpacing)
        self.leftMarginBox.setValue(leftMargin)
        self.topMarginBox.setValue(topMargin)
        self.rightMarginBox.setValue(rightMargin)
        self.bottomMarginBox.setValue(bottomMargin)
        self.wordSpacingBox.setValue(wordSpacing)
        self.lindSpacingSigmaBox.setValue(lineSpacingSigma)
        self.fontSizeSigmaBox.setValue(fontSizeSigma)
        self.wordSpacingSigmaBox.setValue(wordSpacingSigma)
        self.endCharsBox.setText(endChars)
        self.perturbXSigmaBox.setValue(perturbXSigma)
        self.perturbYSigmaBox.setValue(perturbYSigma)
        self.perturbThetaSigmaBox.setValue(perturbThetaSigma)


    def addPreset(self):
        presetName, _ = QInputDialog.getText(self,'添加或更新预设','请输入预设名称')

        print(presetName)
        if _ == False:
            return False
        imageName = self.backgroundBox.currentText().replace("'", "''")
        imageSizeX = int(self.backgroundSizeBoxX.text())
        imageSizeY = int(self.backgroundSizeBoxY.text())
        fontName = self.fontPathBox.currentText().replace("'", "''")
        fontSize = self.fontSizeBox.value()
        fontColor = self.fontColorBox.color
        fontColor = (fontColor.red(), fontColor.green(), fontColor.blue())
        lineSpacing = self.lineSpacingBox.value()
        leftMargin = self.leftMarginBox.value()
        topMargin = self.topMarginBox.value()
        rightMargin = self.rightMarginBox.value()
        bottomMargin = self.bottomMarginBox.value()
        wordSpacing = self.wordSpacingBox.value()
        lineSpacingSigma = self.lindSpacingSigmaBox.value()
        fontSizeSigma = self.fontSizeSigmaBox.value()
        wordSpacingSigma = self.wordSpacingSigmaBox.value()
        endChars = self.endCharsBox.text().replace("'", "''")
        perturbXSigma = self.perturbXSigmaBox.value()
        perturbYSigma = self.perturbYSigmaBox.value()
        perturbThetaSigma = self.perturbThetaSigmaBox.value()

        cursor = self.conn.cursor()
        result = cursor.execute('''select name from %s where name = '%s';''' % (self.presetTableName, presetName.replace("'", "''"))).fetchone()
        if result == None: # 如果没有重名的预设
            maxIdItem = cursor.execute('''select id from %s order by id desc;''' % (self.presetTableName)).fetchone()
            if maxIdItem == None:
                maxId = 0
            else:
                maxId = maxIdItem[0]
            print(maxId)
            cursor.execute('''insert into %s (id, name, useBackgroundImage, imageName, 
                                            backgroundSizeBoxX, backgroundSizeBoxY, fontName, fontSize, 
                                            fontColor, lineSpacing, leftMargin, topMargin, 
                                            rightMargin, bottomMargin, wordSpacing, lineSpacingSigma, 
                                            fontSizeSigma, wordSpacingSigma, endChars, perturbXSigma, 
                                            perturbYSigma, perturbThetaSigma) 
                                    values (%s, '%s', %s, '%s', 
                                            %s, %s, '%s', %s, 
                                            '%s', %s, %s, %s, 
                                            %s, %s, %s, %s, 
                                            %s, %s, '%s', %s, 
                                            %s, %s);'''
                   % (self.presetTableName, maxId+1, presetName, self.useBackgroundImage, imageName,
                                            imageSizeX, imageSizeY, fontName, fontSize,
                                            fontColor, lineSpacing, leftMargin, topMargin,
                                            rightMargin, bottomMargin, wordSpacing, lineSpacingSigma,
                                            fontSizeSigma, wordSpacingSigma, endChars, perturbXSigma,
                                            perturbYSigma, perturbThetaSigma))
        else: # 如果有重名的预设
            answer = QMessageBox.question(self, '更新预设', '已经存在相同名字的预设，是否更新？', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if answer != QMessageBox.Yes:
                return False
            print(answer)
            cursor.execute('''update %s set useBackgroundImage=%s, imageName='%s', 
                                            backgroundSizeBoxX=%s, backgroundSizeBoxY=%s, fontName='%s', fontSize=%s, 
                                            fontColor='%s', lineSpacing=%s, leftMargin=%s, topMargin=%s, 
                                            rightMargin=%s, bottomMargin=%s, wordSpacing=%s, lineSpacingSigma=%s, 
                                            fontSizeSigma=%s, wordSpacingSigma=%s, endChars='%s', perturbXSigma=%s, 
                                            perturbYSigma=%s, perturbThetaSigma=%s where name = '%s' '''
                    % (self.presetTableName, self.useBackgroundImage, imageName,
                                            imageSizeX, imageSizeY, fontName, fontSize,
                                            fontColor, lineSpacing, leftMargin, topMargin,
                                            rightMargin, bottomMargin, wordSpacing, lineSpacingSigma,
                                            fontSizeSigma, wordSpacingSigma, endChars, perturbXSigma,
                                            perturbYSigma, perturbThetaSigma, presetName))
            QMessageBox.information(self, '成功', '预设更新成功')
        self.conn.commit()
        self.refreshList()

    def delPreset(self):
        currentRow = self.presetList.currentRow()
        if currentRow < 0:
            return False
        currentItemName = self.presetList.item(currentRow).text()
        answer = QMessageBox.question(self, '删除预设', '确认要删除“%s”预设吗？' % currentItemName)
        if answer == QMessageBox.No:
            return False
        id = self.conn.cursor().execute('''select id from %s where name = '%s'; ''' % (self.presetTableName, currentItemName)).fetchone()[0]
        self.conn.cursor().execute("delete from %s where id = '%s'; " % (self.presetTableName, id))
        self.conn.cursor().execute("update %s set id=id-1 where id > %s" % (self.presetTableName, id))
        self.conn.commit()
        self.refreshList()

    def upMovePreset(self):
        currentRow = self.presetList.currentRow()
        if currentRow < 1:
            return False
        currentItemName = self.presetList.currentItem().text().replace("'", "''")
        id = self.conn.cursor().execute(
            "select id from %s where name = '%s'" % (self.presetTableName, currentItemName)).fetchone()[0]
        self.conn.cursor().execute("update %s set id=10000 where id=%s-1 " % (self.presetTableName, id))
        self.conn.cursor().execute("update %s set id = id - 1 where name = '%s'" % (self.presetTableName, currentItemName))
        self.conn.cursor().execute("update %s set id=%s where id=10000 " % (self.presetTableName, id))
        self.conn.commit()
        self.refreshList()
        self.presetList.setCurrentRow(currentRow - 1)

    def downMovePreset(self):
        currentRow = self.presetList.currentRow()
        totalRow = self.presetList.count()
        if currentRow < 0 or currentRow > totalRow - 2:
            return False
        currentItemName = self.presetList.currentItem().text().replace("'", "''")
        id = self.conn.cursor().execute(
            "select id from %s where name = '%s'" % (self.presetTableName, currentItemName)).fetchone()[0]
        self.conn.cursor().execute("update %s set id=10000 where id=%s+1 " % (self.presetTableName, id))
        self.conn.cursor().execute("update %s set id = id + 1 where name = '%s'" % (self.presetTableName, currentItemName))
        self.conn.cursor().execute("update %s set id=%s where id=10000 " % (self.presetTableName, id))
        self.conn.commit()
        self.refreshList()
        if currentRow < totalRow:
            self.presetList.setCurrentRow(currentRow + 1)
        else:
            self.presetList.setCurrentRow(currentRow)

    def run(self):
        if not self.checkOutputPath(): # 如果输出检查发生了错误 就停止
            return False
        if self.fontPathBox.currentText() == '':
            QMessageBox.information(self, '字体问题', '选择的字体为空，运行停止。请将 ttf 格式的字体放到本软件根目录的 fonts 文件夹中，再重新启动软件。')
            return False
        if self.useBackgroundImage:
            imageName = self.backgroundBox.currentText()  # 图片文件名
            if imageName == '':
                QMessageBox.warning(self, '背景问题', '你选择了使用图片背景，但背景图片文件为空，运行停止。请将 jpg、png 格式的图片放到本软件根目录的 backgrounds 文件夹中，再重新启动软件。')
                return False
        if (self.backgroundSizeBoxX.text() == '' or self.backgroundSizeBoxY.text() == '') or (int(self.backgroundSizeBoxX.text()) == 0 or int(self.backgroundSizeBoxY.text()) == 0):
            QMessageBox.warning(self, '背景问题', '背景图片大小错误，请检查')
            return False
        inputText = self.inputBox.toPlainText()
        if inputText == '':
            print('没有输入文字')
            return False

        # 背景图片
        imageSizeX = int(self.backgroundSizeBoxX.text())
        imageSizeY = int(self.backgroundSizeBoxY.text())
        if not self.useBackgroundImage:
            background = Image.new(mode="RGB", size=(imageSizeX, imageSizeY),color=(255, 255, 255))
        else:
            imagePath = self.backgroundBox.currentText()
            if not os.path.isabs(imagePath):
                imagePath = os.path.abspath('./backgrounds/' + imageName)
            try:
                with Image.open(imagePath, 'r') as img:
                    width, height = img.size
                    background = img.resize((width * imageSizeX, height * imageSizeY), resample=Image.LANCZOS)
            except:
                QMessageBox.warning(self, '背景问题', '所选背景图片不是可打开的图片文件')
                return False

        # 字体文件
        fontSize = self.fontSizeBox.value()
        fontName = self.fontPathBox.currentText()
        fontPath = os.path.abspath('./fonts/' + fontName)
        try:
            font = ImageFont.truetype(fontPath, fontSize)
        except:
            QMessageBox.warning(self, '字体问题', '所选字体不是可打开的 ttf 字体文件')
            return False

        fontColor = self.fontColorBox.color
        fontColor = (fontColor.red(), fontColor.green(), fontColor.blue())
        lineSpacing = self.lineSpacingBox.value()
        leftMargin = self.leftMarginBox.value()
        topMargin = self.topMarginBox.value()
        rightMargin = self.rightMarginBox.value()
        bottomMargin = self.bottomMarginBox.value()
        wordSpacing = self.wordSpacingBox.value()
        lineSpacingSigma = self.lindSpacingSigmaBox.value()
        fontSizeSigma = self.fontSizeSigmaBox.value()
        wordSpacingSigma = self.wordSpacingSigmaBox.value()
        endChars = self.endCharsBox.text()
        perturbXSigma = self.perturbXSigmaBox.value()
        perturbYSigma = self.perturbYSigmaBox.value()
        perturbThetaSigma = self.perturbThetaSigmaBox.value()
        showImage = self.showImageBox.isChecked()


        template = Template(
            background=background,
            font=font,
            line_spacing=lineSpacing,
            fill=fontColor,  # 字体“颜色”
            left_margin=leftMargin,
            top_margin=topMargin,
            right_margin=rightMargin,
            bottom_margin=bottomMargin,
            word_spacing=wordSpacing,
            line_spacing_sigma=lineSpacingSigma,  # 行间距随机扰动
            font_size_sigma=fontSizeSigma,  # 字体大小随机扰动
            word_spacing_sigma=wordSpacingSigma,  # 字间距随机扰动
            end_chars=endChars,  # 防止特定字符因排版算法的自动换行而出现在行首
            perturb_x_sigma=perturbXSigma,  # 笔画横向偏移随机扰动
            perturb_y_sigma=perturbYSigma,  # 笔画纵向偏移随机扰动
            perturb_theta_sigma=perturbThetaSigma,  # 笔画旋转偏移随机扰动
        )

        thread = GenerateImagesThread()
        self._thread = thread
        thread.text = inputText
        thread.template = template
        thread.outputPath = self.outputPath
        thread.showImage = showImage
        thread.outputFormat = self.outputFormatBox.currentText()
        thread.bgWidth = imageSizeX
        thread.bgHeight = imageSizeY
        thread.fontSize = fontSize
        thread.leftMargin = leftMargin
        thread.rightMargin = rightMargin
        thread.topMargin = topMargin
        thread.bottomMargin = bottomMargin
        thread.lineSpacing = lineSpacing

        self.logBox.clear()
        self.logBox.show()
        self.progressBar.show()
        self.progressBar.setFormat('正在生成...')

        def on_progress(text):
            self.logBox.appendPlainText(text.strip())
            t = text.strip().replace('\n', '')
            if t:
                self.progressBar.setFormat(t[:30])

        def on_finished():
            self.progressBar.hide()
            thread.deleteLater()

        thread.signal.connect(on_progress)
        thread.finished.connect(on_finished)
        thread.start()

    def preview(self):
        if self.fontPathBox.currentText() == '':
            QMessageBox.information(self, '字体问题', '请先选择字体')
            return
        inputText = self.inputBox.toPlainText()
        if inputText == '':
            QMessageBox.information(self, '预览', '请先输入要预览的文字')
            return

        try:
            imageSizeX = int(self.backgroundSizeBoxX.text())
            imageSizeY = int(self.backgroundSizeBoxY.text())
        except:
            QMessageBox.warning(self, '背景问题', '背景图片大小错误，请检查')
            return

        if not self.useBackgroundImage:
            background = Image.new(mode='RGB', size=(imageSizeX, imageSizeY), color=(255, 255, 255))
        else:
            imageName = self.backgroundBox.currentText()
            if imageName == '':
                QMessageBox.warning(self, '背景问题', '背景图片文件为空')
                return
            imagePath = self.backgroundBox.currentText()
            if not os.path.isabs(imagePath):
                imagePath = os.path.abspath('./backgrounds/' + imageName)
            try:
                with Image.open(imagePath, 'r') as img:
                    width, height = img.size
                    background = img.resize((width * imageSizeX, height * imageSizeY), resample=Image.LANCZOS)
            except:
                QMessageBox.warning(self, '背景问题', '所选背景图片不是可打开的图片文件')
                return

        fontSize = self.fontSizeBox.value()
        fontName = self.fontPathBox.currentText()
        fontPath = os.path.abspath('./fonts/' + fontName)
        try:
            font = ImageFont.truetype(fontPath, fontSize)
        except:
            QMessageBox.warning(self, '字体问题', '所选字体不是可打开的 ttf 字体文件')
            return

        fontColor = self.fontColorBox.color
        fontColor = (fontColor.red(), fontColor.green(), fontColor.blue())

        template = Template(
            background=background,
            font=font,
            line_spacing=self.lineSpacingBox.value(),
            fill=fontColor,
            left_margin=self.leftMarginBox.value(),
            top_margin=self.topMarginBox.value(),
            right_margin=self.rightMarginBox.value(),
            bottom_margin=self.bottomMarginBox.value(),
            word_spacing=self.wordSpacingBox.value(),
            line_spacing_sigma=self.lindSpacingSigmaBox.value(),
            font_size_sigma=self.fontSizeSigmaBox.value(),
            word_spacing_sigma=self.wordSpacingSigmaBox.value(),
            end_chars=self.endCharsBox.text(),
            perturb_x_sigma=self.perturbXSigmaBox.value(),
            perturb_y_sigma=self.perturbYSigmaBox.value(),
            perturb_theta_sigma=self.perturbThetaSigmaBox.value(),
        )

        try:
            images = handwrite(inputText, template)
            previewImage = None
            pageCount = 0
            for im in images:
                if previewImage is None:
                    previewImage = im
                else:
                    im.close()
                pageCount += 1
            if previewImage is None:
                QMessageBox.information(self, '预览', '未能生成预览图片')
                return
            from PIL.ImageQt import ImageQt
            from PySide6.QtGui import QPixmap
            qimage = ImageQt(previewImage)
            pixmap = QPixmap.fromImage(qimage)
        except LayoutError as e:
            msg = str(e)
            if 'width < left_margin + font.size + right_margin' in msg:
                need = self.leftMarginBox.value() + self.fontSizeBox.value() + self.rightMarginBox.value()
                detail = (
                    f'背景宽度不足：\n\n'
                    f'当前背景宽度：{imageSizeX}\n'
                    f'左边距：{self.leftMarginBox.value()}\n'
                    f'字号：{self.fontSizeBox.value()}\n'
                    f'右边距：{self.rightMarginBox.value()}\n'
                    f'至少需要宽度：{need}\n\n'
                    f'请增大背景宽度，或减小边距/字号。'
                )
                QMessageBox.warning(self, '预览 - 布局错误', detail)
            elif 'height < top_margin + line_spacing + bottom_margin' in msg:
                need = self.topMarginBox.value() + self.lineSpacingBox.value() + self.bottomMarginBox.value()
                detail = (
                    f'背景高度不足：\n\n'
                    f'当前背景高度：{imageSizeY}\n'
                    f'上边距：{self.topMarginBox.value()}\n'
                    f'行间距：{self.lineSpacingBox.value()}\n'
                    f'下边距：{self.bottomMarginBox.value()}\n'
                    f'至少需要高度：{need}\n\n'
                    f'请增大背景高度，或减小边距/行间距。'
                )
                QMessageBox.warning(self, '预览 - 布局错误', detail)
            elif 'font.size > line_spacing' in msg:
                detail = (
                    f'字号超出行间距：\n\n'
                    f'字号：{self.fontSizeBox.value()}\n'
                    f'行间距：{self.lineSpacingBox.value()}\n\n'
                    f'行间距必须 ≥ 字号，请增大行间距或减小字号。'
                )
                QMessageBox.warning(self, '预览 - 布局错误', detail)
            else:
                QMessageBox.warning(self, '预览 - 布局错误', f'{msg}\n\n请检查尺寸和边距设置。')
            return
        except Exception as e:
            QMessageBox.warning(self, '预览出错', f'{type(e).__name__}: {e}')
            return

        infoText = f'第一页预览（共 {pageCount} 页）' if pageCount > 1 else '共 1 页'

        dialog = QDialog(self)
        dialog.setWindowTitle('预览')
        dialog.resize(800, 600)
        layout = QVBoxLayout(dialog)
        infoLabel = QLabel(infoText)
        infoLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(infoLabel)
        label = QLabel()
        label.setPixmap(pixmap.scaled(760, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        closeBtn = QPushButton('关闭')
        closeBtn.clicked.connect(dialog.accept)
        layout.addWidget(closeBtn, 0, Qt.AlignCenter)
        dialog.exec()
        previewImage.close()




    def checkOutputPath(self):
        self.outputPath = self.outputPathBox.text()
        if not os.path.exists(self.outputPath): # 如果输出路径不存在
            respond = QMessageBox.question(self, '路径错误', '输出文件夹不存在，是否创建？', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if respond == QMessageBox.Yes:
                try:
                    os.mkdir(self.outputPath)
                    return True
                except:
                    QMessageBox.warning(self, '路径错误', '无法创建输出文件夹，请检查输出路径')
                    return False
            else:
                return False # 任务取消
        else:
            return True # 路径存在, 继续任务

    def browseOutputPath(self):
        dirPath = QFileDialog.getExistingDirectory(self, '选择输出文件夹', self.outputPathBox.text())
        if dirPath:
            self.outputPathBox.setText(dirPath.replace('\\', '/'))

    def openOutputPath(self):
        path = self.outputPathBox.text().strip()
        if path.startswith('file://'):
            from urllib.parse import urlparse
            path = urlparse(path).path
        if not os.path.isdir(path):
            QMessageBox.warning(self, '路径错误', f'输出路径不存在：{path}')
            return
        import subprocess
        if sys.platform == 'win32':
            subprocess.run(['explorer', path])
        elif sys.platform == 'darwin':
            subprocess.run(['open', path])
        else:
            subprocess.run(['xdg-open', path])

    def loadHideToTrayPreference(self):
        cursor = self.conn.cursor()
        result = cursor.execute('''select value from %s where item = 'hideToTrayWhenHitCloseButton'; ''' % self.preferenceTableName).fetchone()
        if result is None:
            cursor.execute('''insert into %s (item, value) values ('hideToTrayWhenHitCloseButton', 'False') ''' % self.preferenceTableName)
            self.conn.commit()
        else:
            if result[0] == 'True':
                self.hideToSystemTraySwitch.setChecked(True)

    def hideToSystemTraySwitchClicked(self):
        cursor = self.conn.cursor()
        cursor.execute('''update %s set value='%s' where item = 'hideToTrayWhenHitCloseButton';''' % (self.preferenceTableName, str(self.hideToSystemTraySwitch.isChecked())))
        self.conn.commit()

    def updateCharCount(self):
        import string
        text = self.inputBox.toPlainText()
        punct = set(string.punctuation + '，。、！？；：""''（）【】《》—…·～‧．％℃℉　「」『』')
        count = sum(1 for c in text if c not in string.whitespace and c not in punct)
        self.charCountLabel.setText(f'字数：{count}')

    def browseBackground(self):
        filePath, _ = QFileDialog.getOpenFileName(self, '选择背景图片', '', '图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)')
        if filePath:
            currentIndex = self.backgroundBox.findText(filePath)
            if currentIndex >= 0:
                self.backgroundBox.setCurrentIndex(currentIndex)
            else:
                self.backgroundBox.addItem(filePath)
                self.backgroundBox.setCurrentText(filePath)



    # 启用和停用某些选项
    def switchUseable(self):
        if self.backgroundSwitch.isChecked() == False:
            self.backgroundHint.setEnabled(False)
            self.backgroundBox.setEnabled(False)
        else:
            self.backgroundHint.setEnabled(True)
            self.backgroundBox.setEnabled(True)








