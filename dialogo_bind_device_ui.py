# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogo_bind_device.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 183)
        Dialog.setMinimumSize(QtCore.QSize(400, 183))
        Dialog.setMaximumSize(QtCore.QSize(400, 183))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("app_cok.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.lbl_activation_token = QtWidgets.QLabel(Dialog)
        self.lbl_activation_token.setGeometry(QtCore.QRect(20, 40, 91, 16))
        self.lbl_activation_token.setObjectName("lbl_activation_token")
        self.lbl_license_key = QtWidgets.QLabel(Dialog)
        self.lbl_license_key.setGeometry(QtCore.QRect(20, 80, 61, 16))
        self.lbl_license_key.setObjectName("lbl_license_key")
        self.linedit_license_key = QtWidgets.QLineEdit(Dialog)
        self.linedit_license_key.setGeometry(QtCore.QRect(90, 80, 281, 20))
        self.linedit_license_key.setObjectName("linedit_license_key")
        self.linedit_activation_token = QtWidgets.QLineEdit(Dialog)
        self.linedit_activation_token.setGeometry(QtCore.QRect(110, 40, 261, 20))
        self.linedit_activation_token.setObjectName("linedit_activation_token")
        self.pbtn_ok = QtWidgets.QPushButton(Dialog)
        self.pbtn_ok.setGeometry(QtCore.QRect(160, 130, 75, 23))
        self.pbtn_ok.setObjectName("pbtn_ok")
        self.lbl_correo_contacto = QtWidgets.QLabel(Dialog)
        self.lbl_correo_contacto.setGeometry(QtCore.QRect(10, 160, 171, 20))
        self.lbl_correo_contacto.setObjectName("lbl_correo_contacto")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Aj COK Farming Bot"))
        self.lbl_activation_token.setText(_translate("Dialog", "Activation Token:"))
        self.lbl_license_key.setText(_translate("Dialog", "License Key:"))
        self.pbtn_ok.setText(_translate("Dialog", "Ok"))
        self.lbl_correo_contacto.setText(_translate("Dialog", "contact.cokfarmingbot@gmail.com"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

