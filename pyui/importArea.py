# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/importArea.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1003, 534)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 11, 981, 511))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser_import_intro = QtWidgets.QTextBrowser(self.layoutWidget)
        self.textBrowser_import_intro.setObjectName("textBrowser_import_intro")
        self.verticalLayout.addWidget(self.textBrowser_import_intro)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_import = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_import.setObjectName("pushButton_import")
        self.horizontalLayout.addWidget(self.pushButton_import)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_process = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_process.setObjectName("pushButton_process")
        self.horizontalLayout.addWidget(self.pushButton_process)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_date = QtWidgets.QLabel(self.layoutWidget)
        self.label_date.setObjectName("label_date")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_date)
        self.progressBar_date = QtWidgets.QProgressBar(self.layoutWidget)
        self.progressBar_date.setProperty("value", 0)
        self.progressBar_date.setObjectName("progressBar_date")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.progressBar_date)
        self.label_place = QtWidgets.QLabel(self.layoutWidget)
        self.label_place.setObjectName("label_place")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_place)
        self.progressBar_place = QtWidgets.QProgressBar(self.layoutWidget)
        self.progressBar_place.setProperty("value", 0)
        self.progressBar_place.setObjectName("progressBar_place")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.progressBar_place)
        self.label_people = QtWidgets.QLabel(self.layoutWidget)
        self.label_people.setObjectName("label_people")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_people)
        self.progressBar_people = QtWidgets.QProgressBar(self.layoutWidget)
        self.progressBar_people.setProperty("value", 0)
        self.progressBar_people.setObjectName("progressBar_people")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.progressBar_people)
        self.label_thing = QtWidgets.QLabel(self.layoutWidget)
        self.label_thing.setObjectName("label_thing")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_thing)
        self.progressBar_thing = QtWidgets.QProgressBar(self.layoutWidget)
        self.progressBar_thing.setProperty("value", 0)
        self.progressBar_thing.setObjectName("progressBar_thing")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.progressBar_thing)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.textBrowser_import_intro, self.pushButton_import)
        Form.setTabOrder(self.pushButton_import, self.pushButton_process)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.textBrowser_import_intro.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;\">如何使用</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;\">How to use</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">提醒</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600;\">Notice</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">在浏览照片之前，你需要首先导入照片并对其进行处理。等待照片处理任务完成后，重启应用，你就可以随意所欲的浏览和查找照片了。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Before browsing photoes, you should import import them at first. And then use the application to process them automatically. Once the processing task is finished, re-open the application, and you can browser and search as you demand.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600;\">导入</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600;\">Import</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">点击导入，选择包含有照片的文件夹，然后点击确认。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Push Import button, choose a folder which contains your photos, and then push OK button.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600;\">处理</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600;\">Process</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">图片处理过程（尤其是人脸检测和识别）会花费很长的时间，请耐心等待。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Image processing (especially face detection and recognition) may take very long time, please wait patiently.</span></p></body></html>"))
        self.pushButton_import.setText(_translate("Form", "Import"))
        self.pushButton_process.setText(_translate("Form", "Process"))
        self.label_date.setText(_translate("Form", "Date&Week"))
        self.label_place.setText(_translate("Form", "Place"))
        self.label_people.setText(_translate("Form", "People"))
        self.label_thing.setText(_translate("Form", "Thing"))


