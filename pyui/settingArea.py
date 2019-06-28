# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settingArea.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1015, 513)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_notification = QtWidgets.QLabel(Form)
        self.label_notification.setObjectName("label_notification")
        self.verticalLayout_2.addWidget(self.label_notification)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_key = QtWidgets.QLabel(Form)
        self.label_key.setAlignment(QtCore.Qt.AlignCenter)
        self.label_key.setObjectName("label_key")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_key)
        self.lineEdit_key = QtWidgets.QLineEdit(Form)
        self.lineEdit_key.setMinimumSize(QtCore.QSize(350, 0))
        self.lineEdit_key.setMaximumSize(QtCore.QSize(350, 16777215))
        self.lineEdit_key.setToolTip("")
        self.lineEdit_key.setObjectName("lineEdit_key")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_key)
        self.label_sk = QtWidgets.QLabel(Form)
        self.label_sk.setAlignment(QtCore.Qt.AlignCenter)
        self.label_sk.setObjectName("label_sk")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_sk)
        self.lineEdit_sk = QtWidgets.QLineEdit(Form)
        self.lineEdit_sk.setMinimumSize(QtCore.QSize(350, 0))
        self.lineEdit_sk.setMaximumSize(QtCore.QSize(350, 16777215))
        self.lineEdit_sk.setToolTip("")
        self.lineEdit_sk.setObjectName("lineEdit_sk")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_sk)
        self.horizontalLayout.addLayout(self.formLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_setting = QtWidgets.QPushButton(Form)
        self.pushButton_setting.setObjectName("pushButton_setting")
        self.verticalLayout.addWidget(self.pushButton_setting)
        self.pushButton_test = QtWidgets.QPushButton(Form)
        self.pushButton_test.setObjectName("pushButton_test")
        self.verticalLayout.addWidget(self.pushButton_test)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        self.textBrowser_notification = QtWidgets.QTextBrowser(Form)
        self.textBrowser_notification.setObjectName("textBrowser_notification")
        self.verticalLayout_2.addWidget(self.textBrowser_notification)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_notification.setText(_translate("Form", "Input your API Key and Secret key in line boxes above, and then press Setting and Test button to varify if they are valid."))
        self.label_key.setText(_translate("Form", "Key:"))
        self.lineEdit_key.setPlaceholderText(_translate("Form", "#####-#####-#####-#####-#####-#####"))
        self.label_sk.setText(_translate("Form", "Secret Key:"))
        self.lineEdit_sk.setPlaceholderText(_translate("Form", "###############################"))
        self.pushButton_setting.setText(_translate("Form", "Setting"))
        self.pushButton_test.setText(_translate("Form", "Test"))
        self.textBrowser_notification.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">如何申请腾讯lbs API密钥和SK</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">How to apply for Key and Secret Key of Tencent lbs API</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">1. 打开此链接，申请lbs开发密钥。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">1. Open </span><a href=\"https://lbs.qq.com/guides/startup.html\"><span style=\" font-size:12pt; text-decoration: underline; color:#0000ff;\">this URL</span></a><span style=\" font-size:12pt;\">, and apply for your own application Key.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/icon/setting_0.png\" /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">2. 登录管理台，点击“key管理”。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">2. Log in your console page, and click &quot;key管理&quot;.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/icon/setting_1.png\" /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">3. 点击右侧区域的“设置”选项以打开设置页面。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">3. Click &quot;设置&quot; in the right area to open setting page.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/icon/setting_2.png\" /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">4. 选择API调用方式（签名校验），生成SK。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">4. Choose API invoking method and set your Secret Key.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/icon/setting_3.png\" /></p></body></html>"))


from . import images_rc
