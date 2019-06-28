# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/classImageArea.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(940, 429)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(2, 6, 931, 411))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget_image = QtWidgets.QTableWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tableWidget_image.sizePolicy().hasHeightForWidth())
        self.tableWidget_image.setSizePolicy(sizePolicy)
        self.tableWidget_image.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget_image.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget_image.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_image.setShowGrid(False)
        self.tableWidget_image.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_image.setRowCount(0)
        self.tableWidget_image.setColumnCount(0)
        self.tableWidget_image.setObjectName("tableWidget_image")
        self.tableWidget_image.horizontalHeader().setVisible(False)
        self.tableWidget_image.horizontalHeader().setStretchLastSection(False)
        self.tableWidget_image.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableWidget_image)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_first = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_first.setText("")
        self.pushButton_first.setObjectName("pushButton_first")
        self.horizontalLayout.addWidget(self.pushButton_first)
        self.pushButton_previous = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_previous.setText("")
        self.pushButton_previous.setObjectName("pushButton_previous")
        self.horizontalLayout.addWidget(self.pushButton_previous)
        self.label_page_index = QtWidgets.QLabel(self.layoutWidget)
        self.label_page_index.setText("")
        self.label_page_index.setObjectName("label_page_index")
        self.horizontalLayout.addWidget(self.label_page_index)
        self.pushButton_next = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_next.setText("")
        self.pushButton_next.setObjectName("pushButton_next")
        self.horizontalLayout.addWidget(self.pushButton_next)
        self.pushButton_last = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_last.setText("")
        self.pushButton_last.setObjectName("pushButton_last")
        self.horizontalLayout.addWidget(self.pushButton_last)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.pushButton_first, self.pushButton_previous)
        Form.setTabOrder(self.pushButton_previous, self.pushButton_next)
        Form.setTabOrder(self.pushButton_next, self.pushButton_last)
        Form.setTabOrder(self.pushButton_last, self.tableWidget_image)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))


