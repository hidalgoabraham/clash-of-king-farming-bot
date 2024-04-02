# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ventana_licencia.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(392, 174)
        MainWindow.setMinimumSize(QtCore.QSize(392, 174))
        MainWindow.setMaximumSize(QtCore.QSize(392, 174))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("app_cok.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pbtn_bind_device = QtWidgets.QPushButton(self.centralwidget)
        self.pbtn_bind_device.setGeometry(QtCore.QRect(280, 10, 91, 23))
        self.pbtn_bind_device.setObjectName("pbtn_bind_device")
        self.lbl_license_key = QtWidgets.QLabel(self.centralwidget)
        self.lbl_license_key.setGeometry(QtCore.QRect(20, 60, 61, 16))
        self.lbl_license_key.setObjectName("lbl_license_key")
        self.linedit_license_key = QtWidgets.QLineEdit(self.centralwidget)
        self.linedit_license_key.setGeometry(QtCore.QRect(90, 60, 281, 20))
        self.linedit_license_key.setObjectName("linedit_license_key")
        self.pbtn_ok = QtWidgets.QPushButton(self.centralwidget)
        self.pbtn_ok.setGeometry(QtCore.QRect(160, 120, 75, 23))
        self.pbtn_ok.setObjectName("pbtn_ok")
        self.lbl_correo_contacto = QtWidgets.QLabel(self.centralwidget)
        self.lbl_correo_contacto.setGeometry(QtCore.QRect(10, 150, 171, 20))
        self.lbl_correo_contacto.setObjectName("lbl_correo_contacto")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Aj COK Farming Bot"))
        self.pbtn_bind_device.setText(_translate("MainWindow", "Bind this device"))
        self.lbl_license_key.setText(_translate("MainWindow", "License Key:"))
        self.pbtn_ok.setText(_translate("MainWindow", "Ok"))
        self.lbl_correo_contacto.setText(_translate("MainWindow", "contact.cokfarmingbot@gmail.com"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

