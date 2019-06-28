# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/placeArea.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1006, 537)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(6, 7, 991, 521))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_province = QtWidgets.QLabel(self.layoutWidget)
        self.label_province.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_province.setObjectName("label_province")
        self.gridLayout.addWidget(self.label_province, 0, 0, 1, 1)
        self.label_city = QtWidgets.QLabel(self.layoutWidget)
        self.label_city.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_city.setObjectName("label_city")
        self.gridLayout.addWidget(self.label_city, 0, 1, 1, 1)
        self.label_district = QtWidgets.QLabel(self.layoutWidget)
        self.label_district.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_district.setObjectName("label_district")
        self.gridLayout.addWidget(self.label_district, 0, 2, 1, 1)
        self.comboBox_province = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_province.setObjectName("comboBox_province")
        self.gridLayout.addWidget(self.comboBox_province, 1, 0, 1, 1)
        self.comboBox_city = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_city.setObjectName("comboBox_city")
        self.gridLayout.addWidget(self.comboBox_city, 1, 1, 1, 1)
        self.comboBox_district = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_district.setObjectName("comboBox_district")
        self.gridLayout.addWidget(self.comboBox_district, 1, 2, 1, 1)
        self.pushButton_search = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_search.setObjectName("pushButton_search")
        self.gridLayout.addWidget(self.pushButton_search, 1, 3, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_province.setText(_translate("Form", "Province"))
        self.label_city.setText(_translate("Form", "City"))
        self.label_district.setText(_translate("Form", "District"))
        self.pushButton_search.setText(_translate("Form", "Search"))


