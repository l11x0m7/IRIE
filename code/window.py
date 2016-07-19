# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from result import Result
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import IRIE

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
class MainWindow(QtGui.QWidget): 
    
    dialog1_signal = QtCore.pyqtSignal()          #定义一个无参数的信号，串口设定与子站初始化信号
    
    def __init__(self):
        super(MainWindow,self).__init__()
        self.mse = IRIE.MovieSE()
        self.mse.Init()
        
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("From"))
        Form.resize(1000, 700)
        Form.move(200,200)#窗口在桌面显示位置
        #（先注释掉）左上角图标的路径，可以自己定义图标
        #Form.setWindowIcon(QtGui.QIcon('F:\wdq\python\picture.jpg'))

        self.form = Form
        self.pushButton = QtGui.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(860, 40, 100, 30))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.titleEdit = QtGui.QLineEdit(Form)
        self.titleEdit.setGeometry(QtCore.QRect(40, 40, 800, 30))
        self.titleEdit.setObjectName(_fromUtf8("titleEdit"))

        self.textBrowser = QtGui.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(40, 100, 900, 550))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        #信号连接到指定槽
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
       
        
        
    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "DoubanMovie Search Engine", None))
        self.pushButton.setText(_translate("Form", "搜索", None))
        #self.titleEdit.setText(_translate("Form", "主窗体", None))
        
    def on_pushButton_clicked(self):
        #self.form.hide()
        #Form1 = QtGui.QWidget()
        text = unicode(self.titleEdit.text())
        res = unicode(self.mse.QueryFromWindow(text))
        self.textBrowser.clear()
        self.textBrowser.append(res)
        # ui = Result()
        # ui.setupUi(Form1)
        # Form1.show()
        #Form1.exec_()
        #self.form.show()
    
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    Form1 = QtGui.QWidget()
    window = MainWindow()  
    window.setupUi(Form)

    Form.show()   
    sys.exit(app.exec_()) 
    
    pass
