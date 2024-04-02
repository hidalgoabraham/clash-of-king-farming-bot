# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 19:41:20 2022

@author: Hidalgo
"""

import cv2 as cv
from skimage.metrics import structural_similarity as ssim
import pytesseract as tess
tess.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'
# from pytesseract import Output
import numpy as nmp
from difflib import SequenceMatcher
import time
# from ppadb.client import Client
from matplotlib import pyplot as plt
import traceback
import imutils

import PyQt5
import threading
# from uiautomator import Device
import copy

### Funciones

def buscar_app_cok_abrirla(master):
    while True:
        if master.detener: return
        res_app, x_app, y_app = esperar_template('app_cok.png', master, ttl = 2)
       
        if res_app: 
            hacer_click(master.device, x_app, y_app)
            res_logo, x_logo, y_logo = esperar_template('logo_inicio_cok.png', master, ttl = 2)
            if res_logo: break
        else: 
            hacer_swipe(master.device, int(411*master.w/540), int(732*master.h/960), int(92*master.w/540), int(732*master.h/960), t = 250)
                      
        time.sleep(2)
        
def calibrar_en_castillo(master):
    dispositivo = master.device
    
    res_fml, x_fml, y_fml = esperar_template('flecha_menu_lateral.png', master, ttl = None)
    hacer_click(dispositivo, x_fml, y_fml)
    
    res_o, x_o, y_o = esperar_template('overview.png', master, ttl = 10)
    if not res_o: return
    time.sleep(1)
    
    while True:
        resp_e, x_e, y_e = esperar_template('espadita.png', master, ttl = 1, umbral = 70)
        if not resp_e:        
            hacer_swipe(dispositivo, int(260*master.w/540), y_o + int(20*master.h/960), int(260*master.w/540), int(683*master.h/960))
            if master.detener: return
            time.sleep(0.5)
        else:
            break
        
    resp_e, x_e, y_e = esperar_template('espadita.png', master, ttl = None, umbral = 70)    
    hacer_click(dispositivo, int(336*master.w/540), y_e)#click flecha verde
    time.sleep(2)
    if master.detener: return
        
    master.rc = obtener_calibracion(master, 'barracks.png', umbral = 85)
    
    
def calibrar_en_mapa(master):
    dispositivo = master.device
        
    hacer_click(dispositivo, int(master.w/2), int(master.h/2))

    time.sleep(1)
    master.rm = obtener_calibracion(master, 'my_details.png', umbral = 85)
    
    

def cambiar_a_cuenta(master, info_granjas, k):
    dispositivo = master.device
    posicion = info_granjas[k-1]['posicion']
    # K_cuentas = len(info_granjas)

    res_tt, x_tt, y_tt = esperar_template('marca_soberano.png', master, mostrar = False, ttl = None, umbral = 70)
    
    resp_t = False
    while not resp_t:
        hacer_click(dispositivo, int(50*master.w/1080), y_tt) # El soberano
        resp_t, x_t, y_t = esperar_template('tuerquitas.png', master, ttl = 5, mostrar = False)
        if master.detener: return
    
    hacer_click(dispositivo, x_t, y_t) # Tuerquitas

    resp_a, x_a, y_a = esperar_template('account.png', master)
    hacer_click(dispositivo, x_a, y_a) # Account
    
    resp_sa, x_sa, y_sa = esperar_template('switch_account.png', master)
    hacer_click(dispositivo, x_sa, y_sa) # Switch account
    
    resp_g, x_g, y_g = esperar_template('google_play_account.png', master)
    hacer_click(dispositivo, x_g, y_g) # Google Play Account
            
    resp_f, x_f, y_f = esperar_template('flechita_cuentas.png', master, umbral = 80, mostrar = False)
    hacer_click(dispositivo, x_f, y_f) #flechita
    
    esperar_template('flechita_arriba.png', master, umbral = 80)
    
    time.sleep(2)
    
    _, _, yref = esperar_template('flechita_arriba.png', master, umbral = 80, mostrar = False)
    
    
    # raise Exception
    # return
    
    time.sleep(1)
    
    d1 = int(17*master.h/960)
    d2 = int(69*master.h/960)
    d3 = int(60*master.h/960)
           
    # dy = int(58*master.h/960)
    correccion = int(-1*master.h/960) #2
    
    yc = yref

    xc = int(171*master.w/540)
    
    # if K_cuentas > 10: 
    #     yc = int(73*master.h/960)  
    # else: 
    #     yc = int(232*master.h/960)
    #     # res_h, x_h, y_h = esperar_template('google_play_header.png', master, ttl = None, mostrar = False)        
    #     # yc = y_h + int(118*master.h/960)
    #     yc = yref #+ int(18*master.h/1920)
    #     #print(yc)
    
    # if K_cuentas > 10:
    
    ymax = yref + (d1+correccion) + (d2+correccion) +(d3+correccion)*11
    if posicion == 1:
        yc += (d1+correccion)
        
    elif posicion == 2:
        yc += (d1+correccion) + (d2+correccion)
        
    elif posicion > 2: 
        yc += (d1+correccion) + (d2+correccion)
        for i in range(posicion - 2): 
            yc += (d3+correccion)
    
    #Aqui, ver si hace falta hacer swipe, y si es asi, cuantas veces
    if yc > ymax:
        #hacer swipe
        c = 0
        while yc > ymax:
            yc -= (d3+correccion)
            c += 1
            
        for i in range(c):
            hacer_swipe(dispositivo, int(171*master.w/540), yc, int(171*master.w/540), yc - d3, t = 250)
        
    hacer_click(dispositivo, xc, yc)
    
    esperar_template('flechita_cuentas.png', master, umbral = 80)
    time.sleep(1)
    hacer_click(dispositivo, int(265*master.w/540), int(880*master.h/960)) #boton verde de confirmacion cuenta
    
    for i in range(2):       
        resp_ok, x_ok, y_ok = esperar_template('ok.png', master, ttl = None)
        time.sleep(2)
        hacer_click(dispositivo, x_ok, y_ok)


def curar(master):
    dispositivo = master.device
    
    res_fml, x_fml, y_fml = esperar_template('flecha_menu_lateral.png', master, ttl = None)
    hacer_click(dispositivo, x_fml, y_fml)
    
    if master.detener: return
    
    res_o, x_o, y_o = esperar_template('overview.png', master, ttl = 10)
    if not res_o: return
    
    if master.detener: return
    
    resp_h, x_h, y_h = esperar_template('hospital.png', master, ttl = 1)
    if not resp_h:
        hacer_swipe(dispositivo, int(260*master.w/540), int(683*master.h/960), int(260*master.w/540), int(188*master.h/960), t = 50)
        time.sleep(1)
        hacer_swipe(dispositivo, int(260*master.w/540), int(683*master.h/960), int(260*master.w/540), int(188*master.h/960), t = 50)
        time.sleep(1)
        
        esperar_template('hospital.png', master, ttl = 5)
    
        if master.detener: return    
        time.sleep(1) #esperar que termine la animacion
        
    res_h, x_h, y_h = esperar_template('hospital.png', master, ttl = 5, topleft = True)
    if not res_h: 
        res_b, x_b, y_b = esperar_template('flecha2_menu_lateral.png', master, ttl = None)
        if master.detener: return
        hacer_click(dispositivo, x_b, y_b)
        return
       
    res_f, x_f, y_f = template_en_area(dispositivo, 'green_right_arrow.png', 
                                       x_h, y_h, x_h+int(382*master.w/540), y_h+int(85*master.h/960), r = master.r, umbral = 70)
    
    if res_f:
        res_healing, x_healing, y_healing = template_en_area(dispositivo, 'healing.png', x_h, y_h, x_h+int(382*master.w/540), y_h+int(85*master.h/960), r = master.r)
        if res_healing:
            hacer_click(dispositivo, x_f, y_f) #click a la flecha verde
        else:
            #Curar
            hacer_click(dispositivo, x_f, y_f) #click a la flecha verde
            time.sleep(5)
            
            
            res_hf, x_hf, y_hf = esperar_template('heal_flag.png', master, r2 = master.rc, ttl = 2)
            
            if not res_hf:
                exit_png = cv.imread('./Imagenes/Templates/exit.png')
                while True:
                    dispositivo.shell('input keyevent 4') #Back
                    time.sleep(1)                    
                    captura = obtener_cv_screencap(dispositivo)
                    res_e, x_e, y_e = template_in_image(exit_png, captura, r = master.r)                    
                    if res_e:
                        dispositivo.shell('input keyevent 4') #Back
                        return
                                            
            if master.detener: return
            time.sleep(2) #esperar que termine la animacion
            res_hf, x_hf, y_hf = esperar_template('heal_flag.png', master, r2 = master.rc, ttl = None)
            if master.detener: return
            hacer_click(dispositivo, x_hf, y_hf) #click on heal_flag
            res_hb, x_hb, y_hb = esperar_template('heal_button.png', master)
            if master.detener: return
            hacer_click(dispositivo, x_hb, y_hb) #click en el boton de curar
            
            res_c, x_c, y_c = esperar_template('cancel.png', master, ttl = 2)
            if master.detener: return
            if res_c: hacer_click(dispositivo, x_c, y_c)
            
            time.sleep(2) #esperar que termine la animacion
            if master.detener: return
            quitar_publicidad_si_la_hay(dispositivo, master)
            esperar_template('panel_en_castillo.png', master, ttl = None)
        
    else:
        res_b, x_b, y_b = esperar_template('flecha2_menu_lateral.png', master, ttl = None)
        if master.detener: return
        hacer_click(dispositivo, x_b, y_b)
    


def cv_crop(cv_image, xi, yi, xf, yf):
    crop_img = cv_image[yi:yf, xi:xf]
    return crop_img


def donar_alianza(master):
    dispositivo = master.device
    
    cantidad_de_R = 3
    
    res_a, x_a, y_a = esperar_template('alianza.png', master, ttl = None)
    hacer_click(dispositivo, x_a, y_a)
    
    res_sc, x_sc, y_sc = esperar_template('science_donation.png', master, ttl = 5)
    if res_sc:
        hacer_click(dispositivo, x_sc, y_sc)
        
        for k in range(1, cantidad_de_R+1):
            if master.detener: return
            for i in range(3): 
                if master.detener: return
                hacer_swipe(dispositivo, int(450*master.w/540), int(100*master.h/960), int(450*master.w/540), int(910*master.h/960), t = 100) #Para posicionarse al inicio (arriba) del menu
            for i in range(1, cantidad_de_R+1): #Minimizar todas las R
                if master.detener: return
                resp_r, x_r, y_r = esperar_template('R'+str(i)+'.png', master, ttl = 5) #Ver si esa R esta en pantalla
                if resp_r: #23
                    res_fa, x_fa, y_fa = template_en_area(dispositivo, 'flecha_abajo.png',
                                                          int(480*master.w/540), y_r-int(30*master.h/960), 
                                                          int(530*master.w/540), y_r+int(30*master.h/960), r = master.r)
                    if res_fa: hacer_click(dispositivo, x_fa, y_fa) #Minimizar esa R
            
            #Abrir la R que queremos
            res_r, x_r, y_r = esperar_template('R'+str(k)+'.png', master, ttl = 5) #Ver si esa R esta en pantalla
            if res_r:
                hacer_click(dispositivo, x_r, y_r) #Maximizar la R
                c = 0
                while c < len(master.alliance_science_and_donation['R'+str(k)]):
                    if master.detener: return
                    ruta_template = master.alliance_science_and_donation['R'+str(k)][c]
                    x_t, y_t = ubicacion_template_en_lista(master, ruta_template, umbral = 70)
                    hacer_click(dispositivo, x_t, y_t) #entrar en ese template, esa ciencia
                    time.sleep(2)
                    donacion_completa = hacer_clicks_para_donar(master)

                    if donacion_completa is None:
                        for i in range(2): dispositivo.shell('input keyevent 4') #Back
                        for i in range(2):
                            res_f, x_f, y_f = esperar_template('indicador_publicidad_flecha.png', master, ttl = None)
                            hacer_click(dispositivo, x_f, y_f)
                        esperar_template('panel_en_castillo.png', master, ttl = None)
                        return
                    
                    if type(donacion_completa) == int:
                        if donacion_completa == 1:
                            for i in range(2): dispositivo.shell('input keyevent 4') #Back                            
                            res_e, _, _ = esperar_template('exit.png', master, ttl = 5)
                            if res_e: dispositivo.shell('input keyevent 4') #Back
                            esperar_template('panel_en_castillo.png', master, ttl = None)
                            return
                        
                        if donacion_completa == 4: continue
                            
                                                
                    if donacion_completa:
                        for i in range(2): dispositivo.shell('input keyevent 4') #Back
                        for i in range(2):
                            res_f, x_f, y_f = esperar_template('indicador_publicidad_flecha.png', master, ttl = None)
                            hacer_click(dispositivo, x_f, y_f)
                        esperar_template('panel_en_castillo.png', master, ttl = None)
                        return
                    
                    c += 1
                                                                                        
    else:
        res_f, x_f, y_f = esperar_template('indicador_publicidad_flecha.png', master, ttl = None)
        hacer_click(dispositivo, x_f, y_f)
        esperar_template('panel_en_castillo.png', master, ttl = None)
        

def entrenar(master):
    dispositivo = master.device
    
    res_fml, x_fml, y_fml = esperar_template('flecha_menu_lateral.png', master, ttl = None)
    hacer_click(dispositivo, x_fml, y_fml)
    
    res_o, x_o, y_o = esperar_template('overview.png', master, ttl = 10)
    if not res_o: return
    
    resp_c, x_c, y_c = esperar_template('carrito.png', master, ttl = 1)
    if not resp_c:
        if master.detener: return
        hacer_swipe(dispositivo, int(260*master.w/540), y_o + int(20*master.h/960), int(260*master.w/540), int(683*master.h/960)) #188
        esperar_template('carrito.png', master, ttl = None)
        if master.detener: return
        time.sleep(0.5)
        resp_c, x_c, y_c = esperar_template('carrito.png', master, ttl = None)
        if master.detener: return
   
    hacer_click(dispositivo, int(336*master.w/540), y_c)#click flecha verde
    time.sleep(2)
    if master.detener: return
    resp_s, _, _ = esperar_template('speed_up.png', master, ttl = 2, r2 = master.rc, umbral = 70)
    if not resp_s:
        resp_t, x_t, y_t = esperar_template('train.png', master, ttl = 2, r2 = master.rc)
        if master.detener: return
        
        if not resp_t: return
        
        hacer_click(dispositivo, x_t, y_t)
        time.sleep(5)
        
        # marca_asedio = cv.imread('./Imagenes/Templates/marca_asedio.png')[:]
        # _, wma, hma = marca_asedio.shape[::-1]        
        # marca_asedio = imutils.resize(marca_asedio, width = round(wma*master.r))
        # _, wma, hma = marca_asedio.shape[::-1]
        
        # # captura = obtener_cv_screencap(dispositivo)
        # # resp_ma, x_ma, y_ma = template_in_image(marca_asedio, captura, r = 1, mostrar = True)
        # resp_ma, x_ma, y_ma = template_en_area(dispositivo, 'marca_asedio.png', 
        #                                        int(master.w/2), 0, master.w, master.h, r = master.r, mostrar = True)
        
        # if not resp_ma: 
        #     dispositivo.shell('input keyevent 4') #Back
        #     return
        
        for i in range(9):
            # res_a, x_a, y_a = template_en_area(dispositivo, 'assault_cart.png', 
            #                                    int(410*master.w/540), int(323*master.h/960), 
            #                                    int(494*master.w/540), int(385*master.h/960), r = master.r, mostrar = True)
            
            res_a, x_a, y_a = esperar_template('assault_cart.png', master, ttl = 1, umbral = 85, mostrar = False)
            
            if res_a: break
            if master.detener: return
            # hacer_click(dispositivo, x_ma, y_ma + hma) #bajar
            # hacer_click(dispositivo, int(716*master.w/1080), int(1228*master.h/2340)) #bajar            
            hacer_swipe(dispositivo, int(0.75*master.w), int(0.625*master.h), 
                        int(0.75*master.w), int(0.375*master.h), t = 250) #bajar
            # hacer_click(dispositivo, int(453*master.w/540), int(481*master.h/960))   #bajar
            time.sleep(0.5) #animacion
            
        if not res_a: #hacer_click(dispositivo, int(470*master.w/540), int(273*master.h/960)) #subir
            # hacer_click(dispositivo, x_ma, y_ma - hma) #subir
            # hacer_click(dispositivo, int(716*master.w/1080), int(747*master.h/2340)) #subir
            hacer_swipe(dispositivo, int(0.75*master.w), int(0.375*master.h), 
                        int(0.75*master.w), int(0.625*master.h), t = 250) #subir
            # time.sleep(0.5) #animacion
            # hacer_swipe(dispositivo, int(453*master.w/540), master.w - int(240*master.h/2340), 
            #             int(453*master.w/540), master.w + int(240*master.h/2340), t = 250) #subir
        res_t2, x_t2, y_t2 = esperar_template('train2.png', master, ttl = 5)
        if not res_t2:
            dispositivo.shell('input keyevent 4') #Back
            return
        hacer_click(dispositivo, x_t2, y_t2)
        res_c, x_c, y_c = esperar_template('cancel.png', master, ttl = 5) # con ttl = 2, se quedo pegado
        if res_c: hacer_click(dispositivo, x_c, y_c)
        res_p, x_p, y_p = esperar_template('panel_en_castillo.png', master, ttl = 0.5)
        if master.detener: return
        if not res_p:
            hacer_click(dispositivo, int(264*master.w/540), int(102*master.h/960))
            dispositivo.shell('input keyevent 4') #Back
            
    else:
        res_o, x_o, y_o = esperar_template('overview.png', master, ttl = 5)
        if res_o:
            res_fml, x_fml, y_fml = esperar_template('flecha2_menu_lateral.png', master, ttl = None)
            hacer_click(dispositivo, x_fml, y_fml)

        
                   
def enviar_equipo_al_mundo(master, recurso, level):
    
    dispositivo = master.device
    
    while True:
    
        res_b, x_b, y_b = esperar_template('abrir_busqueda.png', master, ttl = 5, umbral = 80, mostrar = False) # 94.77 es lo que consigue cuando el icono esta totalmente despejado
        if master.detener: return False
        if res_b:
            pass
                        
        else:
            #Para eliminar la flecha negra
            if master.detener: return False
            res_c, x_c, y_c = esperar_template('icono_castillo.png', master, ttl = None)
            hacer_click(dispositivo, x_c, y_c) #click castillo
            if master.detener: return False
            esperar_template('icono_mapa.png', master, ttl = 2) #25
            for i in range(2): quitar_publicidad_si_la_hay(dispositivo, master)
            
            if master.detener: return False
            res_m, x_m, y_m = esperar_template('icono_mapa.png', master, ttl = None)
            
            while True:
                hacer_click(dispositivo, x_m, y_m) #click mapa
                
                if master.detener: return False
                res_c, _, _ = esperar_template('icono_castillo.png', master, ttl = 30)
                if res_c: break
            
            if master.detener: return False
                        
        while True:
            if master.detener: return False
            time.sleep(2) #esperar que la posicion del boton se estabilice   
            res_b, x_b, y_b = esperar_template('abrir_busqueda.png', master, ttl = None)        
            hacer_click(dispositivo, x_b, y_b) #abrir boton de busqueda
            time.sleep(2) #esperar que pasen las animaciones
            
            varios = ['busqueda.png', 'corona.png', 'icono_castillo.png']
            
            indice_vt, x_vt, y_vt = esperar_varios_templates(varios, master, ttl = None)
            if indice_vt is None:
                pass
            else:
                if indice_vt == 0: break
                elif indice_vt == 1: dispositivo.shell('input keyevent 4') #Back
                elif indice_vt == 2: pass
                time.sleep(0.5)
            
        
        if master.detener: return False
        res_bb, x_bb, y_bb = esperar_template('busqueda.png', master, ttl = 5)
        
        if not res_bb: continue
        
        if master.detener: return False
        res_m, x_m, y_m = esperar_template('recurso_madera.png', master, ttl = None) 
        hacer_click(dispositivo, x_m, y_m) #click en madera
        
        if recurso == 'Food': 
            if master.detener: return False
            res_r, x_r, y_r = esperar_template('recurso_alimento.png', master, ttl = None) 
            hacer_click(dispositivo, x_r, y_r) #click en recurso
            
        elif recurso == 'Wood':
            if master.detener: return False
            res_r, x_r, y_r = esperar_template('recurso_madera.png', master, ttl = None) 
            hacer_click(dispositivo, x_r, y_r) #click en recurso
            
        elif recurso == 'Iron': 
            if master.detener: return False
            res_r, x_r, y_r = esperar_template('recurso_hierro.png', master, ttl = None) 
            hacer_click(dispositivo, x_r, y_r) #click en recurso
            
        elif recurso == 'Mithril': 
            if master.detener: return False
            res_r, x_r, y_r = esperar_template('recurso_mithril.png', master, ttl = None) 
            hacer_click(dispositivo, x_r, y_r) #click en recurso
          
        if master.detener: return False              
        
        time.sleep(1)
        
        #obtener el level actual
        try:
            varios = ['level1.png', 'level2.png', 'level3.png', 'level4.png', 'level5.png', 'level6.png', 'level7.png', 'level8.png']
            res_v, _, _ = esperar_varios_templates(varios, master, umbral = 90, mostrar = False)
            
            if res_v is None: level_actual = 1000
            else: level_actual = res_v + 1
            
        except:
            traceback.print_exc()
            level_actual = 1000
        
        if level != level_actual:
            plus = cv.imread('./Imagenes/Templates/plus.png')[:]
            _, wp, hp = plus.shape[::-1]        
            plus = imutils.resize(plus, width = round(wp*master.r))
            _, wp, hp = plus.shape[::-1]
            
            captura = obtener_cv_screencap(dispositivo)
            resp_p, x_p, y_p = template_in_image(plus, captura, r = 1, TopLeft = False, mostrar = False)
            
            hacer_click(dispositivo, x_p + wp, y_p) #click en casilla level
            time.sleep(2) #tarda en responder
            
            if master.detener: return False
            dispositivo.shell('input keyevent 67') #Del
            dispositivo.shell('input text ' + str(level))
            dispositivo.shell('input keyevent 66') #Enter
           
            if master.detener: return False             
            time.sleep(2)
        
        if master.detener: return False
        hacer_click(dispositivo, x_bb, y_bb) #click boton verde de busqueda
        
        if master.detener: return False
        esperar_template('panel_en_mapa.png', master, ttl = None)
        
        hacer_click(dispositivo, int(270*master.w/540), int(482*master.h/960)) # click mina de mundo (esta centrada)
        
        if master.detener: return False
        res_o, x_o, y_o = esperar_template('ocupar.png', master, ttl = 15, umbral = 60, r2 = master.rm, mostrar = False)
        
        if not res_o: return None
        
        hacer_click(dispositivo, x_o, y_o) # click ocupar
        
        varios_templates = ['march.png', 'no_hay_mas_equipos.png']            
        i_temp, x_temp, y_temp = esperar_varios_templates(varios_templates, master, ttl = None)
        
        if master.detener: return False
        
        if i_temp == 0: #march
            no_soldiers_in_city = cv.imread('./Imagenes/Templates/no_soldiers_in_city.png')
            captura = obtener_cv_screencap(dispositivo)
            resp_nsc, x_nsc, y_nsc = template_in_image(no_soldiers_in_city, captura, r = master.r) 
            
            if master.detener: return False
            
            if resp_nsc: 
                dispositivo.shell('input keyevent 4') #Back
                return False
            
            hacer_click(dispositivo, int(438*master.w/540), int(920*master.h/960)) # click marchar
            return True
        
        elif i_temp == 1: #no_hay_mas_equipos
            dispositivo.shell('input keyevent 4') #Back
            return False

            
def enviar_equipo_a_supermina(master):
    
    dispositivo = master.device
    
    res_a, x_a, y_a = esperar_template('alianza.png', master, ttl = None)
    hacer_click(dispositivo, x_a, y_a) #alianza
    
    res_t, x_t, y_t = esperar_template('territorio_alianza.png', master, ttl = 5)
    if not res_t: return False
    hacer_click(dispositivo, x_t, y_t) #territorio
 
    res_s, x_s, y_s = esperar_template('super_mina_alianza.png', master, ttl = None)
    hacer_click(dispositivo, x_s, y_s) #supermina alianza
    
    time.sleep(1)
    hacer_click(dispositivo, x_s, y_s) #anti bug alianza supermina 
    time.sleep(1)
    hacer_click(dispositivo, x_s, y_s) #anti bug alianza supermina
    time.sleep(1)
             
    res_si, _, _ = esperar_template('alliance_supermine_menu_indicator.png', master, ttl = 3)
    if not res_si: 
        hacer_click(dispositivo, x_s, y_s) #supermina alianza
        time.sleep(1)
    
    esperar_template('alliance_supermine_menu_indicator.png', master, ttl = None)
    
    lupa_supermina = cv.imread('./Imagenes/Templates/lupa_supermina.png')[:]
    _, w_lsm, h_lsm = lupa_supermina.shape[::-1]        
    lupa_supermina = imutils.resize(lupa_supermina, width = round(w_lsm*master.r))
    _, w_lsm, h_lsm = lupa_supermina.shape[::-1]
    res_lsm, x_lsm, y_lsm = esperar_template('lupa_supermina.png', master, ttl = 30, canny = True)

    if res_lsm:
        hacer_click(dispositivo, x_lsm + 2*w_lsm, y_lsm) #coordenadas supermina 
        
        esperar_template('rollito_supermina.png', master, ttl = None, r2 = master.rm, mostrar = False, canny = True)
                    
        # Verificar si supermina esta ocupada
        icono_supermina_recolectar = cv.imread('./Imagenes/Templates/icono_supermina_recolectar.png')
        captura = obtener_cv_screencap(dispositivo)
        if master.detener: return
        resp_sm, x_sm, y_sm = template_in_image(icono_supermina_recolectar, captura, mostrar = False, r = master.r*master.rm, canny = True)                
        if resp_sm: 
            hacer_click(dispositivo, x_sm, y_sm) #click recolectar
            
            if master.detener: return
            res_m, _, _ = esperar_template('march.png', master, ttl = 10)
            
            if not res_m: 
                dispositivo.shell('input keyevent 4') #Back
                return
            
            no_soldiers_in_city = cv.imread('./Imagenes/Templates/no_soldiers_in_city.png')
            captura = obtener_cv_screencap(dispositivo)
            resp_nsc, x_nsc, y_nsc = template_in_image(no_soldiers_in_city, captura, r = master.r) 
            if master.detener: return
            
            if resp_nsc: 
                dispositivo.shell('input keyevent 4') #Back
                return
                                
            hacer_click(dispositivo, int(438*master.w/540), int(920*master.h/960)) # click marchar
        
        else:
            dispositivo.shell('input keyevent 4') #Back
            return
        
    
    else:
        dispositivo.shell('input keyevent 4') #Back
        dispositivo.shell('input keyevent 4') #Back
        return
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # dispositivo = master.device
    
    # if master.detener: return
    # res_a, x_a, y_a = esperar_template('alianza.png', master, ttl = None)
    # hacer_click(dispositivo, x_a, y_a) #alianza
    
    # if master.detener: return
    # res_t, x_t, y_t = esperar_template('territorio_alianza.png', master, ttl = None)
    # hacer_click(dispositivo, x_t, y_t) #territorio
 
    # if master.detener: return
    # res_s, x_s, y_s = esperar_template('super_mina_alianza.png', master, ttl = None)
    # hacer_click(dispositivo, x_s, y_s) #supermina alianza
    
    # for i in range(1): hacer_click(dispositivo, x_s, y_s) #anti bug alianza supermina
    # if master.detener: return
    # esperar_template('alliance_supermine_menu_indicator.png', master, ttl = None)
            
    # #ver cual es el recurso disponible en la supermina
    # marcador_supermina_inactiva = cv.imread('./Imagenes/Templates/marcador_supermina_inactiva.png')
    # cr = [] #Coordenadas de rectangulos
    # cr.append([int(32*master.w/540), int(454*master.h/960), int(171*master.w/540), int(694*master.h/960), 'alimento'])
    # cr.append([int(203*master.w/540), int(454*master.h/960), int(336*master.w/540), int(694*master.h/960), 'madera'])
    # cr.append([int(372*master.w/540), int(454*master.h/960), int(504*master.w/540), int(694*master.h/960), 'hierro'])
    # cr.append([int(32*master.w/540), int(708*master.h/960), int(171*master.w/540), int(948*master.h/960), 'mithril'])
    
    # for i in range(len(cr)):
    #     if master.detener: return
    #     recorte = obtener_recorte(dispositivo, cr[i][0], cr[i][1], cr[i][2], cr[i][3])
    #     resp, x, y = template_in_image(marcador_supermina_inactiva, recorte, r = master.r)
    #     if resp:
    #         pass #Mina inactiva
    #     else:
    #         #Mina activa
    #         x = round((cr[i][0]+cr[i][2])/2)
    #         y = cr[i][1] + int(201*master.h/960)
    #         hacer_click(dispositivo, x, y) #click las coordenadas de la supermina
    #         if master.detener: return
    #         esperar_template('rollito_supermina.png', master, ttl = None, r2 = master.rm)

    #         icono_supermina_recolectar = cv.imread('./Imagenes/Templates/icono_supermina_recolectar.png')
    #         captura = obtener_cv_screencap(dispositivo)
    #         resp_sm, x_sm, y_sm = template_in_image(icono_supermina_recolectar, captura, mostrar = False, r = master.r*master.rm)                
    #         hacer_click(dispositivo, x_sm, y_sm) #click recolectar
            
    #         if master.detener: return
    #         esperar_template('march.png', master, ttl = None)
            
    #         no_soldiers_in_city = cv.imread('./Imagenes/Templates/no_soldiers_in_city.png')
    #         captura = obtener_cv_screencap(dispositivo)
    #         resp_nsc, x_nsc, y_nsc = template_in_image(no_soldiers_in_city, captura, r = master.r) 
    #         if master.detener: return
            
    #         if resp_nsc: 
    #             dispositivo.shell('input keyevent 4') #Back
    #             return
                                
    #         hacer_click(dispositivo, int(438*master.w/540), int(920*master.h/960)) # click marchar
    #         break


def esperar_template(archivo_template, master, ttl = 60, mostrar = False, topleft = False, umbral = 80, r2 = 1, canny = False):
    ti = time.time()
    template = cv.imread('./Imagenes/Templates/'+archivo_template)
    while True: 
        if master.detener: return False, None, None
        if ttl is None: pass
        elif (time.time() - ti) > ttl: return False, None, None
        
        captura = obtener_cv_screencap(master.device)
        res, x, y = template_in_image(template, captura, mostrar = mostrar, TopLeft = topleft, umbral = umbral, r = master.r*r2, canny = canny)
        if res: return res, x, y   
        
        
def esperar_varios_templates(archivos_templates, master, ttl = 60, mostrar = False, topleft = False, umbral = 80, r2 = 1, canny = False):
    ti = time.time()
    templates = []
    for archivo in archivos_templates: templates.append(cv.imread('./Imagenes/Templates/'+archivo))
    while True:
        if master.detener: return None, None, None
        if ttl is None: pass
        elif (time.time() - ti) > ttl: return None, None, None
        
        captura = obtener_cv_screencap(master.device)
        
        for i in range(len(templates)):
            if master.detener: return None, None, None
            
            res, x, y = template_in_image(templates[i], captura, mostrar = mostrar, TopLeft = topleft, umbral = umbral, r = master.r*r2, canny = canny)
            if res: return i, x, y 
                

        

def guardar_recuadro(dispositivo, xi, yi, xf, yf, ruta=''):
    captura_cv = obtener_cv_screencap(dispositivo)
    recorte = cv_crop(captura_cv, xi, yi, xf, yf)
    cv.imwrite(ruta, recorte)


def hacer_doble_swipe(dispositivo, x1i, y1i, x1f, y1f, x2i, y2i, x2f, y2f, t = 1000):
    hilo1 = threading.Thread(target = hacer_swipe, args=(dispositivo, x1i, y1i, x1f, y1f, t,))
    hilo2 = threading.Thread(target = hacer_swipe, args=(dispositivo, x2i, y2i, x2f, y2f, t,))
    
    hilo1.start()
    time.sleep(0.5)
    hilo2.start()
    
    while True:
        if (not hilo1.is_alive()) and (not hilo1.is_alive()): break


def hacer_click(dispositivo, x, y):
    dispositivo.shell('input touchscreen tap ' + str(x) + ' ' + str(y))
    

def hacer_clicks_para_donar(master):
    dispositivo = master.device
    
    templates = ['auto_donate.png','increase_max_membership.png']
        
    res_t, x_t, y_t = esperar_varios_templates(templates, master, ttl = 5)    
    
    if res_t is None:
        hacer_click(dispositivo, int(261*master.w/540), int(31*master.h/960))
        return False
    
    if res_t == 1:
        hacer_click(dispositivo, int(261*master.w/540), int(31*master.h/960))
        return False
            
    time_to_wait = 0.5
    
    templates2 = ['resources.png',
                  'earn_gold.png',
                  'stop_donation.png',
                  'auto_donate.png',
                  'alliance_science_and_donation.png']
        
    while True:
        
        if master.detener: return True
        
        res_ta_d, x_ta_d, y_ta_d = template_en_area(dispositivo, 'donation_empty_button.png', 
                                                    int(294*master.w/540), int(669*master.h/960), 
                                                    int(474*master.w/540), int(726*master.h/960), r = master.r) # boton derecho
        if res_ta_d:
            res_ta_i, x_ta_i, y_ta_i = template_en_area(dispositivo, 'donation_empty_button.png', 
                                                        int(63*master.w/540), int(669*master.h/960), 
                                                        int(245*master.w/540), int(726*master.h/960), r = master.r) # boton izquierdo
            if res_ta_i:
                hacer_click(dispositivo, int(270*master.w/540), int(601*master.h/960)) # boton arriba
                time.sleep(time_to_wait)
                if master.detener: return True
                                                
                res_t2, x_t2, y_t2 = esperar_varios_templates(templates2, master, ttl = 20, umbral = 70)  

                if res_t2 == 0: return None
                if res_t2 == 1: return 1
                if res_t2 == 2: return True
                if res_t2 == 3: pass
                if res_t2 == 4: return 4
                                
            else:
                hacer_click(dispositivo, int(150*master.w/540), int(688*master.h/960)) # boton izquierdo 698
                time.sleep(time_to_wait)
                if master.detener: return True
                res_t2, x_t2, y_t2 = esperar_varios_templates(templates2, master, ttl = 20, umbral = 70)  

                if res_t2 == 0: return None
                if res_t2 == 1: return 1
                if res_t2 == 2: return True
                if res_t2 == 3: pass
                if res_t2 == 4: return 4
        else:
            hacer_click(dispositivo, int(384*master.w/540), int(688*master.h/960)) # boton derecho
            time.sleep(time_to_wait)
            if master.detener: return True
            res_t2, x_t2, y_t2 = esperar_varios_templates(templates2, master, ttl = 20, umbral = 70)  

            if res_t2 == 0: return None
            if res_t2 == 1: return 1
            if res_t2 == 2: return True
            if res_t2 == 3: pass
            if res_t2 == 4: return 4

    
def hacer_swipe(dispositivo, xi, yi, xf, yf, t = 100):
    """
    t en milisegundos xD
    umbral aprox 100 ms para swipe rapido/lento
    """
    dispositivo.shell('input touchscreen swipe '+str(xi)+' '+str(yi)+' '+str(xf)+' '+str(yf)+' '+str(t))


def obtener_calibracion(master, archivo_template, umbral = 90, mostrar = False):
    dispositivo = master.device
    
    ccv_template = cv.imread('./Imagenes/Templates/'+archivo_template)[:]
    ccv_image = obtener_cv_screencap(dispositivo)   
    copia_cv_image = ccv_image[:]
    
    dont_care, wo, ho = ccv_template.shape[::-1]
    dont_care, wmax, hmax = copia_cv_image.shape[::-1]
        
    #Ajusta el tamaño del template a la resolución actual del dispositivo
    ccv2_template = imutils.resize(ccv_template, width = round(wo*master.r))
    
    dont_care, wi, hi = ccv2_template.shape[::-1]
        
    copia_cv_image = cv.cvtColor(copia_cv_image, cv.COLOR_BGR2GRAY)
    # copia_cv_image = cv.Canny(copia_cv_image, 50, 200) #si se usa esto, usar umbral 50
    
    ccv2_template = cv.cvtColor(ccv2_template, cv.COLOR_BGR2GRAY)                
    # ccv2_template = cv.Canny(ccv2_template, 50, 200) #si se usa esto, usar umbral 50
    
    ri = 1+50/100
    rf = 1-50/100
    step = -1/100
    
    r2 = ri
    while r2 >= rf:
        
        if master.detener: break
    
        ccv22_template = imutils.resize(ccv2_template[:], width = round(wi*r2))
        wf, hf = ccv22_template.shape[::-1]
        
        # Apply template Matching
        res = cv.matchTemplate(copia_cv_image, ccv22_template, cv.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        
        top_left = max_loc
        x = top_left[0]
        y = top_left[1]
        crop_img = copia_cv_image[y:y+hf, x:x+wf]
        pse = round(porcentaje_similitud_estructural(ccv22_template, crop_img), 2)
                
        # mostrar = True
        if mostrar:            
            texto = 'Template. '
            texto += f'Umbral: {umbral}\n'
            texto += f'pse: {pse}\n'
            texto += f'r2: {str(round(r2, 5))}\n'
            texto += f'X={x}, Y={y}\n'
            texto += f'Width = {wf}, Heigh = {hf}'
            
            copia2_cv_image = copy.deepcopy(ccv_image)
                                                            
            bottom_right = (top_left[0] + wf, top_left[1] + hf)
            cv.rectangle(copia2_cv_image, top_left, bottom_right, 255, -1)
            plt.subplot(121), plt.imshow(copia2_cv_image, cmap = 'gray')
            # plt.title(f'pse: {pse}'), plt.xticks([]), plt.yticks([])
            plt.xticks([]), plt.yticks([])
            plt.subplot(122), plt.imshow(ccv22_template, cmap = 'gray')
            plt.title(texto), plt.xticks([]), plt.yticks([])
            plt.show()
        
        
        
        if pse > umbral: break
    
        r2 += step
        
    return r2


def obtener_cv_screencap(dispositivo):
    captura_bytearray = dispositivo.screencap() 
    captura_cv = cv.imdecode(nmp.frombuffer(captura_bytearray, nmp.uint8), 1)
    return captura_cv


def obtener_equipos_disponibles(master): 
    
    dispositivo = master.device
    
    #entrar al estandarte
    for i in range(2):
        hacer_swipe(dispositivo, int(100*master.w/540), int(700*master.h/960), int(400*master.w/540), int(200*master.h/960), t = 100) # ir abajo izquierda
    
    while True:
        if master.detener: return None, None
        res_e, x_e, y_e = esperar_template('estandarte.png', master, ttl = 3, r2 = master.rc, canny = True)
        
        if not res_e:
            hacer_swipe(dispositivo, int(master.w/2), int(master.h/2), int(master.w/2), int(5*master.h/8), t = 500)
        
        if res_e: 
            hacer_click(dispositivo, x_e, y_e)
            res_t, x_t, y_t = esperar_template('troop_details.png', master, ttl = None, mostrar = False, r2 = master.rc)
            if res_t: 
                hacer_click(dispositivo, x_t, y_t)
                break
    
    esperar_template('troop_details_2.png', master, ttl = None, mostrar = False)
    
    esperar_template('upper_limit.png', master, ttl = 10, mostrar = False)
    esperar_template('upper_limit.png', master, ttl = None, mostrar = False)
    
    captura = obtener_cv_screencap(dispositivo)    
    template = cv.imread('./Imagenes/Templates/no_troops_in_castle.png')
    
    res, a, b = template_in_image(template, captura, r = master.r)
    
    if res:
        equipos_disp = None
        equipos_totales = None
        texto = 'No hay tropas en el castillo'
        master.NuevoMensaje.emit('No troops in castle')
        
    else:    
        
        total_marching = cv.imread('./Imagenes/Templates/total_marching.png')[:]
        _, wtm, htm = total_marching.shape[::-1]        
        total_marching = imutils.resize(total_marching, width = round(wtm*master.r))
        _, wtm, htm = total_marching.shape[::-1]
        
        
        while True:
            captura = obtener_cv_screencap(dispositivo)
            resp_tm, x_tm, y_tm = template_in_image(total_marching, captura, r = 1, TopLeft = True, mostrar = False)
            if resp_tm: break
            
        recorte = obtener_recorte(dispositivo, x_tm, y_tm, x_tm+2*wtm, y_tm+3*htm)
        # cv.imshow('img', recorte)
        texto = tess.image_to_string(recorte)
        # texto = texto.replace(' ', '')
        # master.NuevoMensaje.emit('Texto: ' + texto)
        # texto = texto[15:]
        # master.NuevoMensaje.emit('Total marching: ' + texto)
        # print('Total marching: ' + texto)
                
        try:
            texto = texto[15:]
            texto1 = texto[0:texto.index('/')]
            texto2 = texto[texto.index('/')+1:]
        except:
            texto1 = '5'
            texto2 = '5'
            
        try:
            equipos_disp = int(texto1)
            equipos_totales = int(texto2)
            
        except ValueError:
            equipos_disp = 5
            equipos_totales = 5
        
    #salir del estandarte    
    dispositivo.shell('input keyevent 4') #Back
    
    return equipos_disp, equipos_totales, texto
    

def obtener_recorte(dispositivo, xi, yi, xf, yf):
    captura_cv = obtener_cv_screencap(dispositivo)
    recorte = cv_crop(captura_cv, xi, yi, xf, yf)
    return recorte
    
def porcentaje_similitud_estructural(cv_img1, cv_img2):  
        
    img1 = cv_img1
    img2 = cv_img2
    
    (score, diff) = ssim(img1, img2, full=True)    
    return score*100

def porcentaje_similitud_strings(str_a, str_b):
    return SequenceMatcher(None, str_a, str_b).ratio()*100

def quitar_publicidad_si_la_hay(dispositivo, master):
    
    icono_mapa = cv.imread('./Imagenes/Templates/icono_mapa.png')
    
    c = 0 
    while True:
        
        if master.detener: return
        
        captura = obtener_cv_screencap(dispositivo)
        resp_x, x_x, y_x = template_in_image(icono_mapa, captura, umbral = 90, r = master.r) #95
        
        if resp_x:
            break
        else:
            c+=1
            dispositivo.shell('input keyevent 4') #Back
            # print('Back ' + str(c))
            time.sleep(0.5)
                
                
def recolectar(master, info_granjas, k, equipos_disp, equipos_totales):
    
    recurso = info_granjas[k-1]['recurso']
    level = info_granjas[k-1]['level']
    dispositivo = master.device
               
    if equipos_disp == 0:
        return
    
    if equipos_disp == 1:
        if info_granjas[k-1]['gather_sm']: 
            supermina = super_mine_can_gather(master)
        else: 
            supermina = False
            res_m, x_m, y_m = esperar_template('icono_mapa.png', master, ttl = None)
            hacer_click(dispositivo, x_m, y_m) #click mapa
            esperar_template('panel_en_mapa.png', master, ttl = None)

        if not supermina: 
            there_are_troops = None
            while there_are_troops is None: there_are_troops = enviar_equipo_al_mundo(master, recurso, level)
            if not there_are_troops: return
                        
        else:
            enviar_equipo_a_supermina(master)
    
    if equipos_disp > 1:
        if info_granjas[k-1]['gather_sm']: 
            supermina = super_mine_can_gather(master)
        else: 
            supermina = False
            res_m, x_m, y_m = esperar_template('icono_mapa.png', master, ttl = None)
            hacer_click(dispositivo, x_m, y_m) #click mapa
            esperar_template('panel_en_mapa.png', master, ttl = None)
                                
        if not supermina:
            for j in range(equipos_disp): 
                there_are_troops = None
                while there_are_troops is None: there_are_troops = enviar_equipo_al_mundo(master, recurso, level)
                if not there_are_troops: return
                        
        else:
            for j in range(equipos_disp-1): 
                there_are_troops = None
                while there_are_troops is None: there_are_troops = enviar_equipo_al_mundo(master, recurso, level)
                if not there_are_troops: return
            enviar_equipo_a_supermina(master)
            
 
def reparar_muro(master):
    dispositivo = master.device
    for i in range(2): 
        if master.detener: return
        hacer_swipe(dispositivo, int(100*master.w/540), int(700*master.h/960), int(400*master.w/540), int(200*master.h/960), t = 100)
        time.sleep(1)
        
    # hacer_click(dispositivo, int(500*master.w/540), int(565*master.h/960))
    
    varios = ['pedazo_muro1.png', 'pedazo_muro2.png']#, 'pedazo_muro3.png']
    res_m, x_m, y_m = esperar_varios_templates(varios, master, ttl = 5, mostrar = False, r2 = master.rc, canny = True)

    if res_m is None: 
        hacer_swipe(dispositivo, int(3*master.w/4), int(master.h/2), int(2*master.w/4), int(master.h/2), t = 500)
        time.sleep(1) #animacion
        res_m, x_m, y_m = esperar_varios_templates(varios, master, ttl = 5, mostrar = False, r2 = master.rc, canny = True)

        if res_m is None: 
            return
        else:
            hacer_click(dispositivo, x_m, y_m)
       
    else:
        hacer_click(dispositivo, x_m, y_m)
    

    resp_d, x_d, y_d = esperar_template('defend.png', master, ttl = 30, umbral = 70, r2 = master.rc, mostrar = False)
    if not resp_d: return
    hacer_click(dispositivo, x_d, y_d)
    esperar_template('city_defense.png', master, ttl = None)
    
    marca = cv.imread('./Imagenes/Templates/help_wall.png')[:]
    _, wm, hm = marca.shape[::-1]        
    marca = imutils.resize(marca, width = round(wm*master.w/2160))
    _, wm, hm = marca.shape[::-1]
    
    captura = obtener_cv_screencap(dispositivo)
    res_m, x_m, y_m = template_in_image(marca, captura, r = 1, mostrar = False, canny = True)
    
    if res_m:
        hacer_click(dispositivo, round(master.w/4), y_m + round(5.78*hm))
        # print(f'x = {round(master.w/4)}, y = {y_m + round(5.78*hm)}')
    
    
    
    # res_be, x_be, y_be = esperar_template('boton_extinguir.png', master, mostrar = True, canny = True)
    
    # x = int(137*master.w/540); y = int(667*master.h/960)
    
    
    dispositivo.shell('input keyevent 4') #Back #volver a castillo
    while True:
        res_ec, _ ,_ = esperar_template('panel_en_castillo.png', master, ttl = 5)
        if res_ec: break
        else: dispositivo.shell('input keyevent 4') #Back
    
    
            
def super_mine_can_gather(master):
    
    dispositivo = master.device
    
    res_a, x_a, y_a = esperar_template('alianza.png', master, ttl = None)
    hacer_click(dispositivo, x_a, y_a) #alianza
    
    res_t, x_t, y_t = esperar_template('territorio_alianza.png', master, ttl = 5)
    if not res_t: 
        dispositivo.shell('input keyevent 4') #Back
        res_m, x_m, y_m = esperar_template('icono_mapa.png', master, ttl = None)
        hacer_click(dispositivo, x_m, y_m) #click mapa
        esperar_template('panel_en_mapa.png', master, ttl = None)
        return False
    
    hacer_click(dispositivo, x_t, y_t) #territorio
 
    res_s, x_s, y_s = esperar_template('super_mina_alianza.png', master, ttl = None)
    hacer_click(dispositivo, x_s, y_s) #supermina alianza
    
    time.sleep(1)
    hacer_click(dispositivo, x_s, y_s) #anti bug alianza supermina 
    time.sleep(1)
    hacer_click(dispositivo, x_s, y_s) #anti bug alianza supermina
        
    res_mk, _, _ = esperar_template('alliance_supermine_menu_indicator.png', master, ttl = 10)
    
    if not res_mk:
        dispositivo.shell('input keyevent 4') #Back
        dispositivo.shell('input keyevent 4') #Back
        res_m, x_m, y_m = esperar_template('icono_mapa.png', master, ttl = None)
        hacer_click(dispositivo, x_m, y_m) #click mapa
        esperar_template('panel_en_mapa.png', master, ttl = None)
        return False
     
    lupa_supermina = cv.imread('./Imagenes/Templates/lupa_supermina.png')[:]
    _, w_lsm, h_lsm = lupa_supermina.shape[::-1]        
    lupa_supermina = imutils.resize(lupa_supermina, width = round(w_lsm*master.r))
    _, w_lsm, h_lsm = lupa_supermina.shape[::-1]
    res_lsm, x_lsm, y_lsm = esperar_template('lupa_supermina.png', master, ttl = 30, canny = True)
    
    if res_lsm:
        hacer_click(dispositivo, x_lsm + 2*w_lsm, y_lsm) #coordenadas supermina 
        
        esperar_template('rollito_supermina.png', master, ttl = None, r2 = master.rm, canny = True)
                    
        # Verificar si supermina esta ocupada
        icono_supermina_recolectar = cv.imread('./Imagenes/Templates/icono_supermina_recolectar.png')
        captura = obtener_cv_screencap(dispositivo)
        resp_sm, x_sm, y_sm = template_in_image(icono_supermina_recolectar, captura, mostrar = False, r = master.r*master.rm, canny = True)                
        if resp_sm: supermina = True
        else: supermina = False
        return supermina
    
    else:
        return False
        
        
    
    # #ver cual es el recurso disponible en la supermina
    # marcador_supermina_inactiva = cv.imread('./Imagenes/Templates/marcador_supermina_inactiva.png')
    # cr = [] #Coordenadas de rectangulos
    # cr.append([int(32*master.w/540), int(454*master.h/960), int(171*master.w/540), int(694*master.h/960), 'alimento'])
    # cr.append([int(203*master.w/540), int(454*master.h/960), int(336*master.w/540), int(694*master.h/960), 'madera'])
    # cr.append([int(372*master.w/540), int(454*master.h/960), int(504*master.w/540), int(694*master.h/960), 'hierro'])
    # cr.append([int(32*master.w/540), int(708*master.h/960), int(171*master.w/540), int(948*master.h/960), 'mithril'])
    
    # for i in range(len(cr)):
    #     recorte = obtener_recorte(dispositivo, cr[i][0], cr[i][1], cr[i][2], cr[i][3])
    #     resp, x, y = template_in_image(marcador_supermina_inactiva, recorte, r = master.r)
    #     if resp:
    #         pass #Mina inactiva
    #     else:
    #         #Mina activa
    #         x = round((cr[i][0]+cr[i][2])/2)
    #         y = cr[i][1] + int(201*master.h/960)
    #         hacer_click(dispositivo, x, y) #click las coordenadas de la supermina
    #         esperar_template('rollito_supermina.png', master, ttl = None, r2 = master.rm)
            
    #         #time.sleep(3)
            
    #         # Verificar si supermina esta ocupada
    #         icono_supermina_recolectar = cv.imread('./Imagenes/Templates/icono_supermina_recolectar.png')
    #         captura = obtener_cv_screencap(dispositivo)
    #         resp_sm, x_sm, y_sm = template_in_image(icono_supermina_recolectar, captura, mostrar = False, r = master.r*master.rm)                
    #         if resp_sm: supermina = True
    #         else: supermina = False
    #         return supermina
    
    # return False    
  
 
def template_en_area(dispositivo, archivo_template, xi, yi, xf, yf, r, mostrar = False, topleft = False, umbral = 80):
    
    # captura = obtener_cv_screencap(dispositivo)
    # dont_care, wmax, hmax = captura.shape[::-1]    
       
    recorte = obtener_recorte(dispositivo, xi, yi, xf, yf)
    
    template = cv.imread('./Imagenes/Templates/'+archivo_template)
    # dont_care, wi, hi = template.shape[::-1]
    
    # ccv2_template = imutils.resize(template, width = round(wi*r))
    
    res, x, y = template_in_image(template, recorte, r, mostrar, topleft, umbral = umbral)
    
    if res:
        return res, xi+x, yi+y 
    else: 
        return res, None, None       


def template_in_image(cv_template, cv_image, r, mostrar = False, TopLeft = False, umbral = 80, canny = False):
    ccv_template = cv_template[:]
    ccv_image = cv_image[:]
    
    dont_care, wi, hi = ccv_template.shape[::-1]
    dont_care, wmax, hmax = ccv_image.shape[::-1]
        
    #Ajusta el tamaño del template a la resolución actual del dispositivo
    ccv2_template = imutils.resize(ccv_template, width = round(wi*r))
    ccv20_template = ccv2_template
    
    dont_care, wf, hf = ccv2_template.shape[::-1]
        
    ccv_image = cv.cvtColor(ccv_image, cv.COLOR_BGR2GRAY)
    if canny: ccv_image = cv.Canny(ccv_image, 50, 200) #si se usa esto, usar umbral 50
    
    ccv2_template = cv.cvtColor(ccv2_template, cv.COLOR_BGR2GRAY)                
    if canny: ccv2_template = cv.Canny(ccv2_template, 50, 200) #si se usa esto, usar umbral 50
    
    # Apply template Matching
    res = cv.matchTemplate(ccv_image, ccv2_template, cv.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    
    top_left = max_loc
    x = top_left[0]
    y = top_left[1]
    crop_img = ccv_image[y:y+hf, x:x+wf]
    pse = round(porcentaje_similitud_estructural(ccv2_template, crop_img), 2)
    
    if canny: umbral = 25
    
    # mostrar = True
    if mostrar: 
        # print(pse)
        # print(f'X={x}, Y={y}')
        
        texto = 'Template. '
        texto += f'Umbral: {umbral}\n'
        texto += f'pse: {pse}\n'
        texto += f'X={x}, Y={y}'
         
        copia_cv_image = copy.deepcopy(cv_image)
                                
        bottom_right = (top_left[0] + wf, top_left[1] + hf)
        cv.rectangle(copia_cv_image, top_left, bottom_right, 255, -1)
        plt.subplot(121),plt.imshow(copia_cv_image, cmap = 'gray')
        # plt.title(f'pse: {pse}'), plt.xticks([]), plt.yticks([])
        plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(ccv20_template, cmap = 'gray')
        plt.title(texto), plt.xticks([]), plt.yticks([])
        plt.show()
        
        # plt.imshow(copia_cv_image, cmap = 'gray')
        # plt.title(str(pse)), plt.xticks([]), plt.yticks([])
        # plt.show()
        
    
    if pse > umbral: 
        if not TopLeft: return True, round(x+wf/2), round(y+hf/2) # Las coordenadas del centro
        else: return True, x, y #Las coordenadas de la esquina top left
    
    else:
        return False, None, None
    
    
def texto_en_imagen(texto_ref, cv_imagen, umbral = 80):
    #Aquí se puede usar el efecto Canny, para obtener bordes y detectar mejor el texto
    texto = tess.image_to_string(cv_imagen)
    texto = texto.replace(' ', '')
    # print(texto)
    similitud = porcentaje_similitud_strings(texto, texto_ref)
    if similitud > umbral: return True
    else: return False
    
    
def ubicacion_template_en_lista(master, ruta_template, umbral = 80):
    dispositivo = master.device
    while True:
        if master.detener: return None, None
        res_t, x_t, y_t = esperar_template(ruta_template, master, ttl = 5, umbral = umbral)
        if res_t: 
            time.sleep(2)
            res_t, x_t, y_t = esperar_template(ruta_template, master, ttl = 5, umbral = umbral)
            return x_t, y_t
        else:
            hacer_swipe(dispositivo, int(454*master.w/540), int(822*master.h/960), int(454*master.w/540), int(342*master.h/960), t = 200)
 
# def ubicacion_texto_imagen(master, frase, imagen = None):
    
#     if imagen is None:
#         dispositivo = master.device
#         imagen = obtener_cv_screencap(dispositivo)
        
         
#     d = tess.image_to_data(imagen, output_type = Output.DICT)
#     n_boxes = len(d['level'])    
#     palabras = frase.split()  
#     coordenadas = {}
    
#     for palabra in palabras: 
#         coordenadas[palabra] = []
        
#         for i in range(n_boxes):
#             texto = d['text'][i].replace(' ', '')
#             if texto == '': continue
#             print(texto)
#             similitud = porcentaje_similitud_strings(texto, palabra)
#             if similitud > 50:
#                 (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
#                 coordenadas[palabra].append([x, y, w, h])
                
#     print(coordenadas)
    
    
class Master(PyQt5.QtCore.QThread):
    
    NuevoMensaje = PyQt5.QtCore.pyqtSignal(str)
    
    def __init__(self, info_granjas, dispositivo):
        PyQt5.QtCore.QThread.__init__(self)
        self.name = 'Hilo Master'
        
        self.info_granjas = info_granjas
        self.device = dispositivo
        captura = obtener_cv_screencap(self.device)
        dont_care, self.w, self.h = captura.shape[::-1]
        # print(f'{self.w}x{self.h}')
        self.r = self.w/2160
        #Los templates fueron tomados en una resolución de 2160x3840
        
        self.rc = None
        self.rm = None
        
                     
        self.detener = False
      	         
        self.alliance_science_and_donation = {'R1': ['grand_alliance_1.png', 
                                                     'alliance_guild.png',
                                                     'troop_expansion.png',
                                                     'colossal_legion.png',
                                                     'city_defense_construction.png',
                                                     'alliance_defense.png',
                                                     'precious_friendship.png'],
                                              'R2': ['infantry_king.png',
                                                     'cavalry_king.png',
                                                     'bowman_king.png',
                                                     'chariot_king.png',
                                                     'infantry_killer.png',
                                                     'cavalry_killer.png',
                                                     'bowman_killer.png',
                                                     'chariot_killer.png',
                                                     'alliance_institute.png',
                                                     'quick_rally.png',
                                                     'storage_experts.png',
                                                     'armor_piercing_mastery.png',
                                                     'rapid_armor_piercing.png'],
                                              'R3':['grand_alliance_2.png',
                                                    'farm_expert.png',
                                                    'wood_expert.png',
                                                    'iron_expert.png',
                                                    'mithril_expert.png',
                                                    'alliance_guild.png',
                                                    'super_warehouse.png',
                                                    'top_speed.png',
                                                    'embassy_expansion.png',
                                                    'a_helping_hand.png',
                                                    'storage_experts.png',
                                                    'white_list.png']}
        
  
    def run(self):
        # self.rc = 1.3299999999999998
        # self.rm = 1.0499999999999996
        
        # enviar_equipo_a_supermina(self)
        
        # self.rc = 0.9999999999999996
        # self.rm = 1.0499999999999996
        # donar_alianza(self)
        # return
        
        # self.rc = 1.3299999999999998
        # self.rm = 1.0499999999999996
        # # reparar_muro(self)
        # recolectar(self, self.info_granjas, 2, 2, 2)
        # return
        
        
        
        self.NuevoMensaje.emit('Starting, please wait...')
                        
        try:                                
            esperar_template('icono_mapa.png', self, ttl = None, mostrar = False)
            if self.detener: return
            for i in range(2): quitar_publicidad_si_la_hay(self.device, self)
            if self.detener: return                                        
            self.k = 1
        except:           
            self.detener = True
            self.NuevoMensaje.emit('Master has stopped')
            return
            
        # obtener rc, rm
        self.NuevoMensaje.emit('Please wait...')
        calibrar_en_castillo(self)
        res_m, x_m, y_m = esperar_template('icono_mapa.png', self)
        hacer_click(self.device, x_m, y_m)
        time.sleep(2) #tarda en aparecer
        calibrar_en_mapa(self)
        # print(f'rc = {self.rc}\nrm = {self.rm}')
               
        self.NuevoMensaje.emit('Ready to start!')
        
        while not self.detener:  
            try:
                esperar_template('panel_en_mapa.png', self, ttl = None)
                
                #Seleccionar Cuenta
                self.NuevoMensaje.emit('Selecting account ' + str(self.info_granjas[self.k-1]['posicion']))
                cambiar_a_cuenta(self, self.info_granjas, self.k)
                self.NuevoMensaje.emit('Please wait...')
                esperar_template('panel_en_castillo.png', self, ttl = None)
                for i in range(2): 
                    quitar_publicidad_si_la_hay(self.device, self)
                    time.sleep(2)
                
                if self.detener: break
                
                #Curar tropas
                if self.info_granjas[self.k-1]['heal']: 
                    self.NuevoMensaje.emit('Healing troops')
                    curar(self)
                    
                if self.detener: break
                                
                #Donar a la alianza
                if self.info_granjas[self.k-1]['donate']:
                    self.NuevoMensaje.emit('Donating to alliance')
                    donar_alianza(self)
                    
                if self.detener: break
                    
                #Reparar muro
                self.NuevoMensaje.emit('Increasig city defense')
                reparar_muro(self)
                
                if self.detener: break
                
                #Entrenar
                if self.info_granjas[self.k-1]['train']: 
                    self.NuevoMensaje.emit('Training troops')
                    entrenar(self)
                    
                self.NuevoMensaje.emit('')
                                
                eqp_disp, eqp_tot, texto = obtener_equipos_disponibles(self)

                if self.detener: break
                
                if not eqp_disp is None:
                    if eqp_disp != 0: self.NuevoMensaje.emit('Sending to gather')
                    recolectar(self, self.info_granjas, self.k, eqp_disp, eqp_tot)
                
                self.k += 1
                    
                if self.k > len(self.info_granjas): self.k = 1
                
            except:
                traceback.print_exc()
                self.NuevoMensaje.emit('Master has stopped')
                break
            
               

if __name__ == "__main__":
        
    informacion_granjas = []
 
    informacion_granjas.append({'posicion': 1, 'recurso': 'Wood', 'level': 4})    
    informacion_granjas.append({'posicion': 2, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 3, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 4, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 5, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 6, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 7, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 8, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 9, 'recurso': 'Food', 'level': 4})
    informacion_granjas.append({'posicion': 10, 'recurso': 'Food', 'level': 4})

    
    """
    Importante:
    
    El bot farmea en base a todas las cuentas registradas en la lista de google play.
    El atributo 'posicion' en info_granjas es la posicion de la cuenta
    en la lista de cuentas de google play, donde la posicion 1 corresponde
    a la cuenta que esta mas arriba.
    
    """
       
    # time.sleep(2)
    # master = Master(informacion_granjas)
    # master.start()
    
    # while master.isRunning(): 
    #     try: pass
    #     except: master.detener = True
        
    # master.detener = True
    
    # captura = obtener_cv_screencap(master.device)
    # x, y, w, h = ubicacion_texto_imagen(master, frase = 'Infantry Killer', imagen = captura)
    # cv.rectangle(captura, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # cv.imshow('img', captura)
    # cv.waitKey(0)
    
    
    
    
    
