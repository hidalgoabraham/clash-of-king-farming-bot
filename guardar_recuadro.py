# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 05:29:02 2022

@author: PC
"""

from ppadb.client import Client
import cv2 as cv
# import os
# from PIL import Image
# import io
import numpy as nmp

client = Client(host='127.0.0.1', port=5037)
devices = client.devices()
device_0 = devices[0]

def cv_crop(cv_image, xi, yi, xf, yf):
    crop_img = cv_image[yi:yf, xi:xf]
    return crop_img

def obtener_cv_screencap(dispositivo):
    captura_bytearray = dispositivo.screencap() 
    captura_cv = cv.imdecode(nmp.frombuffer(captura_bytearray, nmp.uint8), -1)
    return captura_cv

def guardar_recuadro(dispositivo, xi, yi, xf, yf, ruta=''):
    # captura_bytearray = dispositivo.screencap() 
    # captura_cv = cv.imdecode(nmp.frombuffer(captura_bytearray, nmp.uint8), -1)
    captura_cv = obtener_cv_screencap(dispositivo)
    recorte = cv_crop(captura_cv, xi, yi, xf, yf)
    cv.imwrite(ruta, recorte)
    # captura_bytearray = dispositivo.screencap()    
    # captura_image = Image.open(io.BytesIO(captura_bytearray))
    # captura_image.save('auxiliar.png')
    # recorte = cv_crop(cv.imread('auxiliar.png'), xi, yi, xf, yf)
    # cv.imwrite(ruta, recorte)
    # os.remove('auxiliar.png')
    
    
ruta = './Imagenes/Templates/captura.png'
cv.imwrite(ruta, obtener_cv_screencap(device_0))
    
# guardar_recuadro(device_0, 0, 0, 2160, 3840, 'C:\Users\PC\Documents\Python Scripts\AjCokFarmingBot\Imagenes\Templates/google_play_header.png') #540, 960








