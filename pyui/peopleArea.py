# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/peopleArea.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1004, 531)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(4, 3, 991, 521))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_p1 = QtWidgets.QLabel(self.layoutWidget)
        self.label_p1.setObjectName("label_p1")
        self.horizontalLayout.addWidget(self.label_p1)
        self.lineEdit_p1 = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_p1.setObjectName("lineEdit_p1")
        self.horizontalLayout.addWidget(self.lineEdit_p1)
        self.comboBox_logic = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_logic.setObjectName("comboBox_logic")
        self.comboBox_logic.addItem("")
        self.comboBox_logic.addItem("")
        self.comboBox_logic.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_logic)
        self.label_p2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_p2.setObjectName("label_p2")
        self.horizontalLayout.addWidget(self.label_p2)
        self.lineEdit_p2 = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_p2.setObjectName("lineEdit_p2")
        self.horizontalLayout.addWidget(self.lineEdit_p2)
        self.pushButton_search = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_search.setObjectName("pushButton_search")
        self.horizontalLayout.addWidget(self.pushButton_search)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.lineEdit_p1, self.comboBox_logic)
        Form.setTabOrder(self.comboBox_logic, self.lineEdit_p2)
        Form.setTabOrder(self.lineEdit_p2, self.pushButton_search)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_p1.setText(_translate("Form", "Name"))
        self.lineEdit_p1.setPlaceholderText(_translate("Form", "Enter the first name"))
        self.comboBox_logic.setItemText(0, _translate("Form", "AND"))
        self.comboBox_logic.setItemText(1, _translate("Form", "OR"))
        self.comboBox_logic.setItemText(2, _translate("Form", "NOT"))
        self.label_p2.setText(_translate("Form", "Name"))
        self.lineEdit_p2.setPlaceholderText(_translate("Form", "Enter the second name"))
        self.pushButton_search.setText(_translate("Form", "Search"))


