# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 17:25:32 2022

@author: Hidalgo
"""


import PyQt5
from ventana_principal_ui import Ui_MainWindow as Ui_VentanaPrincipal
from ventana_licencia_ui import Ui_MainWindow as Ui_VentanaLicencia
from dialogo_bind_device_ui import Ui_Dialog as Ui_DialogoBindDevice
from ventana_anuncio_ui import Ui_Dialog as Ui_VentanaAnuncio

from uuid import getnode as get_mac
import requests
import json
# import hashlib

import os
import time
import datetime
import traceback

from Master import Master
from ppadb.client import Client

import subprocess

def ping_test(direccion, mostrar = False):
    
    response = os.system("ping -n 1 " + direccion) #for windows
    # response = os.system("ping -c 1 " + direccion) #for linux
    if mostrar: print(response)
    
    if response == 0: pingstatus = True
    else: pingstatus = False
            
    return pingstatus



def license_is_validated(license_key, account_id):
    """
    Returns: 
        Respuesta: Boolean
        texto: string
        constant: string
    """
    machine_fingerprint = str(get_mac()) #hashlib.sha256(str(get_mac()).encode('utf-8')).hexdigest()
    validation = requests.post(
        "https://api.keygen.sh/v1/accounts/{}/licenses/actions/validate-key".format(account_id),
        headers={
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
            },
        data=json.dumps({
            "meta": {
                "scope": { "fingerprint": machine_fingerprint },
                "key": license_key
                }
            })
        ).json()

    if "errors" in validation:
        errs = validation["errors"]
        texto = "license validation failed: {}".format(
            map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs))
        return False, texto, validation["meta"]["constant"]
    
    # If the license is valid for the current machine, that means it has
    # already been activated. We can return early.
    if validation["meta"]["valid"]:
        texto = "license has already been activated on this machine"
        return True, texto, validation["meta"]["constant"]
    
    if validation["meta"]["constant"] != "NO_MACHINE":
        texto = "license {}".format(validation["meta"]["detail"])
        return False, texto, validation["meta"]["constant"]
    
    else:
        texto = 'license has not been yet activated on this machine'
        return False, texto, validation["meta"]["constant"]
    
    
def lets_activate_license(activation_token, license_key, account_id):
    """
    Returns: 
        Respuesta: Boolean
        texto: string
    """
    machine_fingerprint = str(get_mac()) #hashlib.sha256(str(get_mac()).encode('utf-8')).hexdigest()
    validation = requests.post(
        "https://api.keygen.sh/v1/accounts/{}/licenses/actions/validate-key".format(account_id),
        headers={
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
            },
        data=json.dumps({
            "meta": {
                "scope": { "fingerprint": machine_fingerprint },
                "key": license_key
                }
            })
        ).json()
            
    activation = requests.post(
      "https://api.keygen.sh/v1/accounts/{}/machines".format(account_id),
      headers={
        "Authorization": "Bearer {}".format(activation_token),
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
      },
      data=json.dumps({
        "data": {
          "type": "machines",
          "attributes": {
            "fingerprint": machine_fingerprint
          },
          "relationships": {
            "license": {
              "data": { "type": "licenses", "id": validation["data"]["id"] }
            }
          }
        }
      })
    ).json()
  
    # If we get back an error, our activation failed.
    if "errors" in activation:
        errs = activation["errors"]
        # print(errs)
        # texto = "license activation failed: {}".format(
        #     map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs))
        texto = errs[0]['code']
        return False, texto
  
    return True, "license activated"
    

def segundos_to_string(delta):    
    string = str(datetime.timedelta(seconds=int(delta)))
    return string

class BorrarFilas(PyQt5.QtCore.QThread):

    def __init__(self, layout, fi = None, ff = None):
        PyQt5.QtCore.QThread.__init__(self)
        
        self.layout=layout
        
        if fi is None: self.fi=1
        else: self.fi=fi
        
        if ff is None: self.ff=self.layout.rowCount()
        else: self.ff=ff
        
    def run(self):
        for i in range(self.fi,self.ff+1):
            for j in range(self.layout.columnCount()): 
                try:
                    self.layout.itemAtPosition(i-1,j).widget().deleteLater()
                except:
                    pass
            
    def salir(self):
        self.exit()
  
        
class Cronometro(PyQt5.QtCore.QThread):
    
    def __init__(self, label):
        PyQt5.QtCore.QThread.__init__(self)
        self.name = 'Hilo Cronometro'
        
        self.label = label
        self.detener = False
        
    def run(self):
        ti = time.time()
        while not self.detener:
            time.sleep(1)
            tf = time.time()
            delta = tf - ti
            tiempo_str = segundos_to_string(delta)
            self.label.setText(tiempo_str)
        
        self.label.setText('')
    

class VentanaPrincipal(PyQt5.QtWidgets.QMainWindow, Ui_VentanaPrincipal, PyQt5.QtCore.QObject):
    
    def __init__(self):
        PyQt5.QtWidgets.QMainWindow.__init__(self)
        PyQt5.QtCore.QObject.__init__(self)
        self.setupUi(self)
        
        self.setEnabled(False)
        self.setWindowOpacity(0.0)
                        
        self.keygen_sh_account_id = '9a75811d-8b4c-4fcc-b823-90db211c2c20' #ID de COK Bot en Keygen.sh
        self.dispositivo_vinculado = None
        self.master = None
                
        self.ventana_licencia = VentanaLicencia(self)
        self.ventana_licencia.ValidacionCorrecta.connect(self.ventana_licencia_validacion_correcta)
        self.ventana_licencia.show()
        
        
    def closeEvent(self, event):
        self.salir()
        event.accept()
        
    def salir(self): 
        try: self.master.detener = True
        except: pass
        
        try: self.ventana1.salir()    
        except: pass
    
        self.hide()
        
    def ventana_licencia_validacion_correcta(self):
        self.ventana_licencia.salir()
        
        self.spnbx_Nfarms.setMaximum(999)
        
        self.W = dict()
        self.W['cbx_position1'] = self.cbx_position1
        self.W['cbx_resource1'] = self.cbx_resource1
        self.W['spnbx_level1'] = self.spnbx_level1
        self.W['chbx_heal1'] = self.chbx_heal1
        self.W['chbx_train1'] = self.chbx_train1
        self.W['chbx_donate1'] = self.chbx_donate1
        self.W['chbx_gathersm1'] = self.chbx_gathersm1       
        
        self.maxNfarms = 1
        self.Nfarms_anterior = self.spnbx_Nfarms.value()
        self.spnbx_Nfarms.valueChanged.connect(self.spnbx_Nfarms_value_changed)
        
        self.pbtn_start.clicked.connect(self.pbtn_start_clicked)
        self.pbtn_stop.clicked.connect(self.pbtn_stop_clicked)
        self.pbtn_how_to_use.clicked.connect(self.pbtn_how_to_use_clicked)
        
        self.setEnabled(True)        
        self.setWindowOpacity(1)
        
        # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowState(self.windowState() & ~PyQt5.QtCore.Qt.WindowMinimized | PyQt5.QtCore.Qt.WindowActive)
        self.activateWindow()
        
        self.cronometro = None
        self.licencia = None
        
        
    def borrar_filas(self, layout, fi = None, ff = None): 
        hilo_borrar=BorrarFilas(layout, fi, ff)
        hilo_borrar.start()
        while not hilo_borrar.isFinished(): pass
        hilo_borrar.salir()
        hilo_borrar.deleteLater()
        
    def spnbx_Nfarms_value_changed(self):
        if self.spnbx_Nfarms.value() > self.Nfarms_anterior: #Agregar filas
            self.maxNfarms = self.spnbx_Nfarms.value()
            
            for idn in range(1, self.Nfarms_anterior+1): 
                for j in range(self.Nfarms_anterior+1, self.spnbx_Nfarms.value()+1): 
                    self.W['cbx_position'+str(idn)].addItem(str(j))
            
            for idn in range(self.Nfarms_anterior + 1, self.spnbx_Nfarms.value() + 1):  
                #cbx_position
                self.W['cbx_position'+str(idn)] = PyQt5.QtWidgets.QComboBox()
                self.W['cbx_position'+str(idn)].setMaximumWidth(50)
                for j in range(1, self.spnbx_Nfarms.value()+1): self.W['cbx_position'+str(idn)].addItem(str(j))
                self.W['cbx_position'+str(idn)].setCurrentIndex(self.W['cbx_position'+str(idn-1)].currentIndex()+1)
                
                #cbx_resource
                self.W['cbx_resource'+str(idn)] = PyQt5.QtWidgets.QComboBox()
                self.W['cbx_resource'+str(idn)].setMaximumWidth(60)
                self.W['cbx_resource'+str(idn)].addItem('Food')
                self.W['cbx_resource'+str(idn)].addItem('Wood')
                self.W['cbx_resource'+str(idn)].addItem('Iron')
                self.W['cbx_resource'+str(idn)].addItem('Mithril')
                # self.W['cbx_resource'+str(idn)].setCurrentIndex(0)
                self.W['cbx_resource'+str(idn)].setCurrentText(self.W['cbx_resource'+str(idn-1)].currentText())
                
                #spnbx_level
                self.W['spnbx_level'+str(idn)] = PyQt5.QtWidgets.QSpinBox()
                self.W['spnbx_level'+str(idn)].setMinimum(1)
                self.W['spnbx_level'+str(idn)].setMaximum(8)
                # self.W['spnbx_level'+str(idn)].setValue(4)
                self.W['spnbx_level'+str(idn)].setValue(self.W['spnbx_level'+str(idn-1)].value())
                
                #chbx_gathersm1
                self.W['chbx_gathersm'+str(idn)] = PyQt5.QtWidgets.QCheckBox()
                self.W['chbx_gathersm'+str(idn)].setMaximumWidth(13)
                # self.W['chbx_gathersm'+str(idn)].setChecked(True)
                self.W['chbx_gathersm'+str(idn)].setChecked(self.W['chbx_gathersm'+str(idn-1)].isChecked())

                
                #chbx_heal
                self.W['chbx_heal'+str(idn)] = PyQt5.QtWidgets.QCheckBox()
                self.W['chbx_heal'+str(idn)].setMaximumWidth(13)
                # self.W['chbx_heal'+str(idn)].setChecked(True)
                self.W['chbx_heal'+str(idn)].setChecked(self.W['chbx_heal'+str(idn-1)].isChecked())
                
                #chbx_train
                self.W['chbx_train'+str(idn)] = PyQt5.QtWidgets.QCheckBox()
                self.W['chbx_train'+str(idn)].setMaximumWidth(13)
                # self.W['chbx_train'+str(idn)].setChecked(True)
                self.W['chbx_train'+str(idn)].setChecked(self.W['chbx_train'+str(idn-1)].isChecked())
                
                #chbx_donate
                self.W['chbx_donate'+str(idn)] = PyQt5.QtWidgets.QCheckBox()
                self.W['chbx_donate'+str(idn)].setMaximumWidth(13)
                # self.W['chbx_donate'+str(idn)].setChecked(True)
                self.W['chbx_donate'+str(idn)].setChecked(self.W['chbx_donate'+str(idn-1)].isChecked())
                                                
                self.farms_layout.addWidget(self.W['cbx_position'+str(idn)], idn-1, 0)
                self.farms_layout.addWidget(self.W['cbx_resource'+str(idn)], idn-1, 1)
                self.farms_layout.addWidget(self.W['spnbx_level'+str(idn)], idn-1, 2)
                self.farms_layout.addWidget(self.W['chbx_gathersm'+str(idn)], idn-1, 3, PyQt5.QtCore.Qt.AlignHCenter)
                self.farms_layout.addWidget(self.W['chbx_heal'+str(idn)], idn-1, 4, PyQt5.QtCore.Qt.AlignHCenter)
                self.farms_layout.addWidget(self.W['chbx_train'+str(idn)], idn-1, 5, PyQt5.QtCore.Qt.AlignHCenter)
                self.farms_layout.addWidget(self.W['chbx_donate'+str(idn)], idn-1, 6, PyQt5.QtCore.Qt.AlignHCenter)
                                  
        elif self.spnbx_Nfarms.value() < self.Nfarms_anterior: #Borrar filas
        
            for idn in range(1, self.Nfarms_anterior+1): 
                for j in range(self.spnbx_Nfarms.value()+1, self.Nfarms_anterior+1): 
                    self.W['cbx_position'+str(idn)].removeItem(j-1)
        
            self.borrar_filas(self.farms_layout, self.spnbx_Nfarms.value()+1, self.Nfarms_anterior)
                                    
        self.Nfarms_anterior = self.spnbx_Nfarms.value()
        
    def pbtn_start_clicked(self):
        res_val, texto_val, const_val = license_is_validated(self.licencia, self.keygen_sh_account_id)
        if not res_val:
            texto1 = 'Invalid License Key'
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.salir()
            return
                
        
        #Verificar posiciones
        for i in range(1, self.spnbx_Nfarms.value()+1):
            numero_cuenta = self.W['cbx_position'+str(i)].currentText()
            for j in range(1, self.spnbx_Nfarms.value()+1):
                if j != i:
                    if self.W['cbx_position'+str(j)].currentText() == numero_cuenta:
                        texto1 = 'The positon of an account must not be repeated.'
                        texto2 = 'Please check and correct.'
                        anuncio = VentanaAnuncio(texto1, texto2)
                        anuncio.exec()
                        return
                        
        #Posiciones correctas
        
        self.scrollArea.setEnabled(False)
        self.spnbx_Nfarms.setEnabled(False)
        self.pbtn_how_to_use.setEnabled(False)
        self.cbx_device.setEnabled(False)
        
        #Tomar info_granjas
        
        info_granjas = []
        
        try:
            for i in range(1, self.spnbx_Nfarms.value()+1):
                info_granjas.append({'posicion': int(self.W['cbx_position'+str(i)].currentText()), 
                                     'recurso': self.W['cbx_resource'+str(i)].currentText(), 
                                     'level': self.W['spnbx_level'+str(i)].value(), 
                                     'heal': self.W['chbx_heal'+str(i)].isChecked(), 
                                     'train': self.W['chbx_train'+str(i)].isChecked(), 
                                     'donate': self.W['chbx_donate'+str(i)].isChecked(),
                                     'gather_sm': self.W['chbx_gathersm'+str(i)].isChecked()})
        except ValueError:
            texto1 = 'Some value is invalid.'
            texto2 = 'Please check and correct.'
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.scrollArea.setEnabled(True)
            self.spnbx_Nfarms.setEnabled(True)
            self.pbtn_how_to_use.setEnabled(True)
            self.cbx_device.setEnabled(True)
            return
            
                        
        try:
            if self.cbx_device.currentText() == 'USB device':
                root = os.path.dirname(__file__)
                ruta = os.path.join(root, 'Device_Tools\platform-tools/adb.exe')
                subprocess.Popen([ruta, 'devices'])
                       
            client = Client(host = '127.0.0.1', port = 5037)
            devices = client.devices()
            device_0 = devices[0]
            
            self.master = Master(info_granjas, device_0)
            self.master.NuevoMensaje.connect(self.master_nuevo_mensaje)
                        
        except:
            # traceback.print_exc()
            texto1 = 'An error has occurred.'
            texto2 = 'Please make sure the emulator is started\n'
            texto2 += 'or the device is connected correctly.\n' 
            texto2 += 'Also, verify you have the correct adb driver installed.\n'
            texto2 += 'If the problem persists, restart your PC and try again.'
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            
            self.scrollArea.setEnabled(True)
            self.spnbx_Nfarms.setEnabled(True)
            self.pbtn_how_to_use.setEnabled(True)
            self.cbx_device.setEnabled(True)
            return
            
        self.master.start()
        self.pbtn_start.hide()
        self.pbtn_stop.show()
        
        self.cronometro = Cronometro(self.lbl_crono)
        self.cronometro.start()
    
    def pbtn_stop_clicked(self):          
        # esto tambien se puede implemetar con 
        # QThread.requestInterruption() y
        # QThread.isInterruptionRequested()
        
        
        self.master.detener = True  
        self.master.quit()
        
        # while self.master.isRunning(): pass
        
        self.scrollArea.setEnabled(True)
        self.spnbx_Nfarms.setEnabled(True)
        self.pbtn_how_to_use.setEnabled(True)
        self.cbx_device.setEnabled(True)
        
        self.pbtn_start.show()
        self.pbtn_stop.hide()
        
        self.lbl_prompt.setText('')
        
        self.cronometro.detener = True
        
    def master_nuevo_mensaje(self, texto):
        self.lbl_prompt.setText(texto)
    
    def pbtn_how_to_use_clicked(self):
        texto = '1. Open your Android emulator or connect your device.\n'
        # texto += '2. Set the emulator\'s screen resolution to 540x960.\n'
        texto += '2. Start the C.O.K. app. in the emulator or device.\n'
        texto += '3. In the Bot main screen, add the accounts positions\nand set the parameters to farm.\n'
        texto += '4. Click on the Start button.'
        
        anuncio = VentanaAnuncio(texto)
        anuncio.exec()


class VentanaLicencia(PyQt5.QtWidgets.QMainWindow, Ui_VentanaLicencia, PyQt5.QtCore.QObject):
    
    ValidacionCorrecta = PyQt5.QtCore.pyqtSignal()
    
    def __init__(self, ventana_principal):
        PyQt5.QtWidgets.QMainWindow.__init__(self)
        PyQt5.QtCore.QObject.__init__(self)
        self.setupUi(self)
        
        # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowState(self.windowState() & ~PyQt5.QtCore.Qt.WindowMinimized | PyQt5.QtCore.Qt.WindowActive)
        self.activateWindow()
        
        self.cvp = ventana_principal
        
        self.pbtn_bind_device.clicked.connect(self.pbtn_bind_device_clicked)
        self.pbtn_ok.clicked.connect(self.pbtn_ok_clicked)
        
        #cargar contenido del archivo llkt.txt en el linedit_license_key (last license key typed)
        extension = 'txt'
        ruta = './llkt' + '.' + extension
        if ruta!='':
            if ruta[-(len(extension) +1):] != '.'+extension: ruta=ruta+'.'+extension
                                            
            with open(ruta, "r") as escritor:
                for fila in escritor:
                    self.linedit_license_key.setText(fila)
        
    
    def closeEvent(self, event):
        self.cvp.salir()
        event.accept()
        
    def salir(self):
        self.hide()
        
    def pbtn_bind_device_clicked(self):
        ventana_bind_device = VentanaBindDevice(self.cvp)
        ventana_bind_device.exec()
    
    def pbtn_ok_clicked(self):
                                          
        if self.linedit_license_key.text() == '': 
            texto1 = 'Invalid License Key'
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            return
        
        res_val, texto_val, const_val = license_is_validated(self.linedit_license_key.text(), self.cvp.keygen_sh_account_id)
        
        # print('License is validated: ' + str(res_val))
        # print(texto_val)
        # print(const_val)
        # print('')
                
        
        if res_val: 
            self.ValidacionCorrecta.emit()
            
            extension = 'txt'
            ruta = './llkt' + '.' + extension
            if ruta!='':
                if ruta[-(len(extension) +1):] != '.'+extension: ruta=ruta+'.'+extension
                                                
                with open(ruta, "w") as escritor:
                    escritor.write(self.linedit_license_key.text())
            
            self.cvp.licencia = self.linedit_license_key.text()
            return
        else:
            if const_val == "NO_MACHINE":
                texto1 = 'This device has not been binded yet\nfor the current License Key'
                texto2 = ''
                anuncio = VentanaAnuncio(texto1, texto2)
                anuncio.exec()
                return
            else:
                texto1 = 'Invalid License Key'
                texto2 = ''
                anuncio = VentanaAnuncio(texto1, texto2)
                anuncio.exec()
                return   
            
        


class VentanaBindDevice(PyQt5.QtWidgets.QDialog, Ui_DialogoBindDevice):
    def __init__(self, ventana_principal):
        PyQt5.QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        
        self.cvp = ventana_principal
        self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        
        self.linedit_license_key.setText(self.cvp.ventana_licencia.linedit_license_key.text())
        
        #Conexiones
        self.pbtn_ok.clicked.connect(self.pbtn_ok_clicked)
        
    def closeEvent(self, event):
        event.accept()
        
    def salir(self): self.close()
    
    def pbtn_ok_clicked(self):
        self.setEnabled(False)
        
        if self.linedit_license_key.text() == '': 
            texto1 = 'Invalid License Key'
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.setEnabled(True)
            return
        
        if self.linedit_activation_token.text() == '': 
            texto1 = 'Invalid Activation Token'
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.setEnabled(True)
            return
        
        
        try:
            self.cvp.dispositivo_vinculado, texto_act = lets_activate_license(self.linedit_activation_token.text(),
                                                                              self.linedit_license_key.text(),
                                                                              self.cvp.keygen_sh_account_id)
            
            # print(texto_act)
            
        except TypeError:
            texto1 = 'Invalid License Key and/or Activation Token'
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.setEnabled(True)
            traceback.print_exc()
            return
                        
        if self.cvp.dispositivo_vinculado:
            texto1 = 'This device has been binded successfully'
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.cvp.ventana_licencia.linedit_license_key.setText(self.linedit_license_key.text())
            
        else:            
            texto1 = texto_act
            texto2 = ''
            anuncio = VentanaAnuncio(texto1, texto2)
            anuncio.exec()
            self.setEnabled(True)
            return
        
        self.close() 
        
        
class VentanaAnuncio(PyQt5.QtWidgets.QDialog, Ui_VentanaAnuncio):
    def __init__(self, texto1, texto2 = None):
        PyQt5.QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        
        if texto2 is None: self.lbl.setText(texto1)
        else: self.lbl.setText(texto1 + '\n\n' + texto2)
        
        #Conexiones
        self.pbtn.clicked.connect(self.pbtn_clicked)
        
    def closeEvent(self, event):
        event.accept()
        
    def salir(self): self.close()
    
    def pbtn_clicked(self): self.close()   

    
        
        
        
        
if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication([])
    
    if not ping_test('keygen.sh'):
        texto1 = 'Connection failed.'
        texto2 = ''
        anuncio = VentanaAnuncio(texto1, texto2)
        anuncio.exec()
        
    else:        
                
        ventana_principal = VentanaPrincipal()
        ventana_principal.show()
        
    app.exec_()
            