# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 11:39:14 2024

@author: pc
"""

import cv2
import os
import datetime as dt
import pandas as pd
import numpy as np
from skimage.io import imread
from skimage.color import rgb2lab, lab2rgb
import matplotlib.pylab as plt
import tensorflow
import joblib
from keras.models import load_model
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.pyplot import figure
from tkinter import *
from pathlib import Path
from tkinter import filedialog
from PIL import Image
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from scipy import signal
import csv
from tkinter import messagebox
import tkinter as tk
import matplotlib.colors as mcolors
from matplotlib.colors import Normalize
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from flask import Flask, request, jsonify
from datetime import datetime
import requests
import tkinter as tk
import threading
import requests
import time
from flask import Flask, request
from datetime import datetime
from werkzeug.serving import make_server
from flask import Flask, request
from datetime import datetime, timedelta

raiz= Tk()
raiz.title("Spectrophotometer")


bucle_activo = False
ultima_imagen = ""
hilo_monitoreo = None 

bucle_activo1 = False
hilo_monitoreo1 = None 


# Configuración para guardar las imágenes
SAVE_FOLDER = r'C:\Users\pc\Desktop\universidad\Doctorado\Artículos LAB y IA\camara_arduino\basura'
SAVE_FOLDER1=SAVE_FOLDER
ESP32_IP = 'http://10.142.91.171'  # Dirección IP de la ESP32

    
# Crear la carpeta si no existe
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Servidor Flask para recibir imágenes
app = Flask(__name__)

time1 = 10000  # Por ejemplo, 5 segundos entre cada imagen
last_save_time = datetime.now() - timedelta(seconds=time1)  # Para permitir la primera imagen inmediatamente

@app.route('/upload', methods=['POST'])
def upload_file():
    global last_save_time

    if request.method == 'POST':
        current_time = datetime.now()

        # Verificar si ha pasado el intervalo de tiempo desde la última imagen guardada
        if (current_time - last_save_time).total_seconds() >= time1:
            img = request.data  # El contenido de la imagen vendrá en el cuerpo de la solicitud

            # Generar un nombre único usando la fecha y la hora actual
            timestamp = current_time.strftime('%Y%m%d_%H%M%S')
            image_name = os.path.join(SAVE_FOLDER, f'captura_{timestamp}.jpg')

            # Guarda la imagen en un archivo con un nombre único
            with open(image_name, 'wb') as f:
                f.write(img)

            last_save_time = current_time  # Actualizar el tiempo de la última imagen guardada
            return f"Imagen guardada exitosamente como {image_name}!", 200
        else:
            return "Aún no ha pasado el intervalo de tiempo para guardar una nueva imagen", 200

# Clase para ejecutar el servidor Flask en segundo plano
class FlaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = make_server('0.0.0.0', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

# Variables globales para controlar la captura de imágenes
stop_thread = False

flask_thread = FlaskThread()
flask_thread.start()

def folder():
    
    global name
    
    
    name= filedialog.askdirectory()
     
    example3.set(name)

def tiempo():
    
    
    global time1
    
    time1=float(text_box3.get()) #The time added by the user is saved in the variable "time"
    example2.set(time1) #The time introduced by the user appears in the text box 9
    time1=float(text_box4.get())
    example1.set("")

def landa():
    
    global lamda
    
    lamda=float(text_box6.get()) #The time added by the user is saved in the variable "time"
    landa2.set(lamda) #The time introduced by the user appears in the text box 9
    lamda=float(text_box7.get())
    landa1.set("")

def area():
    
    global x_axis
    global y_axis
    global p
    
    def obtener_primera_imagen():
        
        archivos_iniciales = set(os.listdir(SAVE_FOLDER))  # Archivos antes de la captura
        print("Esperando una nueva imagen...")
    
        # Monitorear la carpeta hasta que aparezca un nuevo archivo
        while True:
            archivos_actuales = set(os.listdir(SAVE_FOLDER))  # Archivos actuales
            nuevos_archivos = archivos_actuales - archivos_iniciales  # Detectar nuevos archivos
            
            if nuevos_archivos:
                nuevo_archivo = nuevos_archivos.pop()  # Obtener el nombre del primer archivo nuevo
                print(f"Nueva imagen encontrada: {nuevo_archivo}")
                return nuevo_archivo
            
            time.sleep(1)  # Esperar un segundo antes de volver a verificar
    
    nueva_imagen = obtener_primera_imagen()
    
    def drawing(event,x,y,flags,param):
        global pixelx1, pixelx2, pixely1, pixely2   #variables that will save pixels of the selected area by the user
        
        
        if event == cv2.EVENT_LBUTTONDOWN: # By clicking the left mouse button, the upper left corner of the area to be studied is selected.
            
            #Pixels in X axis and Y axis are saved in variable "pixelx1" and "pixely1"
            pixelx1=x
            pixely1=y
            #The selected pixels are displayed on the screen
            print ('pixel x1=',x) 
            print ('pixel y1=',y)
        if event == cv2.EVENT_RBUTTONDOWN: # By clicking the right mouse button, the bottom right corner of the area to be studied is selected.
            
            #Pixels in X axis and Y axis are saved in variable "pixelx2" and "pixely2"
            pixelx2=x
            pixely2=y
            #The selected pixels are displayed on the screen
            print ('pixel x2=',x)
            print ('pixel y2=',y)
            cv2.rectangle(image,(pixelx1,pixely1),(pixelx2,pixely2),(255,0,0),1)
    	
    #Code to show the first frame obtained of the video in another window and code necessary to call the previous function
    image = cv2.imread('./basura/'+str(nueva_imagen))
    image_to_study = image.copy() 

    cv2.namedWindow('image_to_study')
    cv2.setMouseCallback('image_to_study',drawing)
    
    while True:
    	cv2.imshow('image_to_study',image)
    	
    	if cv2.waitKey(1) & 0xFF == 27:
    		break

    cv2.destroyAllWindows()
    
    x_axis=abs(pixelx2-pixelx1) #variable to save the number of pixels in x axis from the area selected by the user
    y_axis=abs(pixely2-pixely1)#variable to save the number of pixels in y axis from the area selected by the user
    p=x_axis*y_axis
    #The numbers of pixels in Y and X axis corresponding to the area selected by the user are shown
    print ('x_axis=',x_axis)
    print ('y_axis=',y_axis)
    
    area1.set("Process completed")

def Start():
    
    global SAVE_FOLDER
    global nueva_imagen
    global bucle_activo
    global ultima_imagen
    global hilo_monitoreo
    global s
    
    
    SAVE_FOLDER = name
    s=1
   
    
    def monitorear_carpeta():
        global bucle_activo, ultima_imagen
        global Labim
        global time2
        global spectrum_pred2
        global time_values
        global transmittance_values
        

        
        archivos_iniciales = set(os.listdir(SAVE_FOLDER))
        time2=0
        
        fig, axs = plt.subplots(1, 1, dpi=80, figsize=(7, 5), sharey=True)
        fig.suptitle('Transmittance Evolution', size=20)
        axs.set_xlabel('Time (seconds)', size=12)
        axs.set_ylabel('Transmittance (%)', size=12)
        axs.set_ylim(0, 100)
        
        # Crear la línea vacía que se actualizará en cada iteración
        line, = axs.plot([], [], color='y')
        
        canvas = FigureCanvasTkAgg(fig, master=frame2)
        canvas.get_tk_widget().grid(column=4, row=0, rowspan=30)
        
        # Variables para almacenar el tiempo y los datos de transmittancia
        time_values = []
        transmittance_values = []
        
        dato_t=[]
        dato_e=[]
        
        def update_plot(time2, spectrum_pred2):
            
            
            # Actualizar las listas de datos
            time_values.append(time2)
            transmittance_values.append(100 * spectrum_pred2)
        
            # Actualizar la línea en la gráfica con los nuevos datos
            line.set_data(time_values, transmittance_values)
        
            # Ajustar los límites del eje x según los nuevos valores de tiempo
            axs.set_xlim(min(time_values), max(time_values))
        
            # Volver a dibujar el gráfico
            canvas.draw()
        
        while bucle_activo:
            archivos_actuales = set(os.listdir(SAVE_FOLDER))
            nuevos_archivos = archivos_actuales - archivos_iniciales
            
            if nuevos_archivos:
                ultima_imagen = nuevos_archivos.pop()  # Guardar la última imagen que apareció
                print(f"Nueva imagen: {ultima_imagen}")
                archivos_iniciales = archivos_actuales  # Actualizar los archivos iniciales
                image1= (SAVE_FOLDER)+'/'+(ultima_imagen)
                image2=Image.open(image1)
                Lab3=np.zeros((p,3))
                Labim=np.zeros((1,3))
                c=0
                
                for i in range(y_axis):
                    for j in range(x_axis):
                        r, g, b = image2.getpixel((j+pixelx1,i+pixely1))
                        im1 = sRGBColor(r/255, g/255, b/255)
                        im2= convert_color(im1, LabColor) 
                        Lab3[c,0]=im2.lab_l
                        Lab3[c,1]=im2.lab_a
                        Lab3[c,2]=im2.lab_b
                        c=c+1
                
                L=0
                a=0
                b=0
                for i in range(p):
                    L=L+Lab3[i,0]
                    a=a+Lab3[i,1]
                    b=b+Lab3[i,2]
                
                Labim[0,:] = [L/p,a/p,b/p]
                
                
                nx=61
                Labim_norm1=np.zeros((nx,4))
                Labim_norm2=np.zeros((nx,4))
                y=0
                
                
                for j in range (nx):
                  Labim_norm1[y,0]=Labim[0,0]
                  Labim_norm1[y,1]=Labim[0,1]
                  Labim_norm1[y,2]=Labim[0,2]
                  Labim_norm1[y,3]=400+j*5
                  Labim_norm2[y,0]=Labim_norm1[y,0]/100
                  Labim_norm2[y,1]=(Labim_norm1[y,1]+100)/200
                  Labim_norm2[y,2]=(Labim_norm1[y,2]+100)/200
                  
                  if Labim_norm1[y,3] == 400:
                    Labim_norm2[y,3]=0
                  else:
                    Labim_norm2[y,3]=(Labim_norm1[y,3]-400)/300
          
                  y=y+1
                
                sol_n_n = load_model('Neural_network.h5')
                
                lamda1 = (lamda-400)/300 #user-entered standardized wavelength 
                Labim_norm3=np.zeros((1,4)) #variable to store the results of the neural network when undoing normalization
                t=0
                
                for i in range (nx):
                    if Labim_norm2[i,3] == lamda1:
                        Labim_norm3[0,0]=Labim_norm2[i,0]
                        Labim_norm3[0,1]=Labim_norm2[i,1]
                        Labim_norm3[0,2]=Labim_norm2[i,2]
                        Labim_norm3[0,3]=Labim_norm2[i,3]
                        

                spectrum_pred2=sol_n_n.predict(Labim_norm3)
                
                
                update_plot(time2, spectrum_pred2)
                
                time2=time2+time1
                
            time.sleep(0.25)  # Esperar un segundo entre verificaciones
    
        print("Bucle detenido.")  # Esto se ejecuta cuando se sale del bucle
    
    if SAVE_FOLDER:
        bucle_activo = True
        button7.config(state=tk.DISABLED)  # Desactivar el botón de inicio
        btn_exit.config(state=tk.NORMAL)  # Activar el botón de detener
        # Ejecutar el monitoreo en un nuevo hilo para no bloquear la interfaz
        hilo_monitoreo = threading.Thread(target=monitorear_carpeta)
        hilo_monitoreo.start()
    else:
        messagebox.showerror("Error", "No se ha seleccionado una carpeta.")
    
    
    

def Start1():

    global SAVE_FOLDER
    global nueva_imagen
    global bucle_activo1
    global ultima_imagen
    global hilo_monitoreo1
    global s
    
    
    SAVE_FOLDER = name
    s=2
   
    
    def monitorear_carpeta1():
        global bucle_activo1, ultima_imagen
        global Labim
        global wlength
        global lines
        global spectrum_pred3
        global spectrum_pred4
        global wlength
        global Labim1
        
        wlength=np.zeros((61,1))
        z=0
        for i in range (61):
          wlength[i] = 400 + z
          z=z+5
        
        archivos_iniciales = set(os.listdir(SAVE_FOLDER))

        fig, axs = plt.subplots(1, 1, dpi=80, figsize=(7, 5), sharey=True)
        fig.suptitle('SPECTRUM EVOLUTION', size=20)
        axs.set_xlabel('Wavelength (nm)', size=12)
        axs.set_ylabel('Transmittance (%)', size=12)
        axs.set_ylim(0, 100)  # Ajusta según el rango esperado de tus valores de Y
        
        # Crear una lista vacía para almacenar todas las líneas
        lines = []
        spectrum_pred4=[]
        Labim1=[]
        
        canvas = FigureCanvasTkAgg(fig, master=frame2)
        canvas.get_tk_widget().grid(column=4, row=0, rowspan=30)
        
        def get_random_color():
            """Generar un color aleatorio en formato RGB"""
            return np.random.rand(3,)  # Devuelve un array de 3 valores entre 0 y 1
        
        def update_plot1(espectro_pred3):
            # Representar el nuevo array de Y en el gráfico
            color = get_random_color()
            
            line, = axs.plot(wlength, espectro_pred3*100, color=color, alpha=0.7)
            
            # Guardar la nueva línea en la lista
            lines.append(line)
        
            # Volver a dibujar el gráfico con la nueva línea añadida
            canvas.draw()
        
        while bucle_activo1:
            archivos_actuales = set(os.listdir(SAVE_FOLDER))
            nuevos_archivos = archivos_actuales - archivos_iniciales
            
            if nuevos_archivos:
                ultima_imagen = nuevos_archivos.pop()  # Guardar la última imagen que apareció
                print(f"Nueva imagen: {ultima_imagen}")
                archivos_iniciales = archivos_actuales  # Actualizar los archivos iniciales
                image1= (SAVE_FOLDER)+'/'+(ultima_imagen)
                image2=Image.open(image1)
                Lab3=np.zeros((p,3))
                Labim=np.zeros((1,3))
                c=0
                
                for i in range(y_axis):
                    for j in range(x_axis):
                        r, g, b = image2.getpixel((j+pixelx1,i+pixely1))
                        im1 = sRGBColor(r/255, g/255, b/255)
                        im2= convert_color(im1, LabColor) 
                        Lab3[c,0]=im2.lab_l
                        Lab3[c,1]=im2.lab_a
                        Lab3[c,2]=im2.lab_b
                        c=c+1
                
                L=0
                a=0
                b=0
                for i in range(p):
                    L=L+Lab3[i,0]
                    a=a+Lab3[i,1]
                    b=b+Lab3[i,2]
                
                Labim[0,:] = [L/p,a/p,b/p]
                
                Labim1.append(Labim.flatten())
                
                
                nx=61
                Labim_norm1=np.zeros((nx,4))
                Labim_norm2=np.zeros((nx,4))
                y=0
                                
                
                for j in range (nx):
                  Labim_norm1[y,0]=Labim[0,0]
                  Labim_norm1[y,1]=Labim[0,1]
                  Labim_norm1[y,2]=Labim[0,2]
                  Labim_norm1[y,3]=400+j*5
                  Labim_norm2[y,0]=Labim_norm1[y,0]/100
                  Labim_norm2[y,1]=(Labim_norm1[y,1]+100)/200
                  Labim_norm2[y,2]=(Labim_norm1[y,2]+100)/200
                  
                  if Labim_norm1[y,3] == 400:
                    Labim_norm2[y,3]=0
                  else:
                    Labim_norm2[y,3]=(Labim_norm1[y,3]-400)/300
          
                  y=y+1
                
                sol_n_n = load_model('Neural_network.h5')
                
                spectrum_pred3=sol_n_n.predict(Labim_norm2) #Spectrum result from neural network, in normalized (0 to 1) values
                
                spectrum_pred4.append(spectrum_pred3.flatten())
                
                update_plot1(spectrum_pred3)
                
                
                
            time.sleep(0.25)  # Esperar un segundo entre verificaciones
    
        print("Bucle detenido.")  # Esto se ejecuta cuando se sale del bucle
    
    if SAVE_FOLDER:
        bucle_activo1 = True
        button10.config(state=tk.DISABLED)  # Desactivar el botón de inicio
        btn_exit2.config(state=tk.NORMAL)  # Activar el botón de detener
        # Ejecutar el monitoreo en un nuevo hilo para no bloquear la interfaz
        hilo_monitoreo1 = threading.Thread(target=monitorear_carpeta1)
        hilo_monitoreo1.start()
    else:
        messagebox.showerror("Error", "No se ha seleccionado una carpeta.")
    
def terminar():
    global stop_thread
    stop_thread = True  # Detener el hilo de captura
    flask_thread.shutdown()  # Detener el servidor Flask
    
    
    raiz.destroy() 

def detener():
       
    global bucle_activo, hilo_monitoreo
    global SAVE_FOLDER
    bucle_activo = False
    if hilo_monitoreo:
        hilo_monitoreo.join()  # Esperar a que el hilo termine
    button7.config(state=tk.NORMAL)  # Activar el botón de inicio
    btn_exit.config(state=tk.DISABLED)  # Desactivar el botón de detener
    messagebox.showinfo("Monitoreo detenido", f"Última imagen capturada: {ultima_imagen}")
    
    SAVE_FOLDER=SAVE_FOLDER1
    #global stop_thread
    
    #raiz.destroy()  # Cierra la ventana
    
    #stop_thread = True  # Detener el hilo de captura
    #flask_thread.shutdown()  # Detener el servidor Flask

def detener1():
       
    global bucle_activo1, hilo_monitoreo1
    global SAVE_FOLDER
    bucle_activo1 = False
    if hilo_monitoreo1:
        hilo_monitoreo1.join()  # Esperar a que el hilo termine
    button10.config(state=tk.NORMAL)  # Activar el botón de inicio
    btn_exit2.config(state=tk.DISABLED)  # Desactivar el botón de detener
    messagebox.showinfo("Monitoreo detenido", f"Última imagen capturada: {ultima_imagen}")
    
    SAVE_FOLDER=SAVE_FOLDER1
    #global stop_thread
    
    #raiz.destroy()  # Cierra la ventana
    
    #stop_thread = True  # Detener el hilo de captura
    #flask_thread.shutdown()  # Detener el servidor Flask
    
def Reset():
    
    global SAVE_FOLDER
    global s
    
    s==0
    
    SAVE_FOLDER=SAVE_FOLDER1
    example1.set("")
    example2.set("")
    example3.set("")
    area1.set("")
    landa1.set("")
    landa2.set("")
    save1.set("")
    
    fig, axs = plt.subplots(1, 1, dpi=80, figsize=(7, 5), sharey=True)
    fig.suptitle('', size=20)
    axs.set_xlabel('', size=12)
    axs.set_ylabel('', size=12)
    axs.set_ylim(0, 100)  # Ajusta según el rango esperado de tus valores de Y
    
    # Crear una lista vacía para almacenar todas las líneas
    lines = []
    
    canvas = FigureCanvasTkAgg(fig, master=frame2)
    canvas.get_tk_widget().grid(column=4, row=0, rowspan=30)

def saved():
    global file1
    global transmittance_values1
    global spectrum_pred5
    global Labim2
    
    file1= text_box9.get()
    
    if s==1:
        transmittance_values1=[]
        transmittance_values1=[x[0][0] for x in transmittance_values]
        time3=np.array(time_values)
        spectrum_pred3=np.array(transmittance_values1)
        # dataframes are created to introduces values of the X and Y axis of the resulting graph. These dataframes are neccesary to create the ".csv" file
        df1 = pd.DataFrame(time3)
        df2 = pd.DataFrame(spectrum_pred3)

        # Combines the DataFrames horizontally into a single DataFrame.
        df_combined = pd.concat([df1, df2], axis=1)

        # Specify the name of the CSV file that you want to create.
        file_name = str(file1)+".csv"

        # Save the combined DataFrame in a CSV file.
        df_combined.to_csv(file_name, index=False, header=False)
    
    if s==2:
        # dataframes are created to introduces values of the X and Y axis of the resulting graph. These dataframes are neccesary to create the ".csv" file
        spectrum_pred5=np.column_stack(spectrum_pred4)
        Labim2=np.column_stack(Labim1)
        df1 = pd.DataFrame(wlength)
        df2 = pd.DataFrame(spectrum_pred5)
        df3 = pd.DataFrame(Labim2)

        # Combines the DataFrames horizontally into a single DataFrame.
        df_combined = pd.concat([df1, df2, df3], axis=1)

        # Specify the name of the CSV file that you want to create.
        file_name = str(file1)+".csv"

        # Save the combined DataFrame in a CSV file.
        df_combined.to_csv(file_name, index=False, header=False)   
      
    save1.set("saved")

def show_explanation():
    explanation = """
    - Time Between Images
    Enter the time (in seconds) between each image capture and processed.
    - Press “Enter Data” to confirm.
    The value on the right shows the current interval used by the system.  
    """
    messagebox.showinfo("Time", explanation)

def show_explanation1():
    explanation = """
    - Wavelength (λ_max)
    Enter a wavelength (400–700 nm) for transmittance tracking.
    - Press “Enter Data” to confirm.
    The value on the right shows the selected wavelength.
    """
    messagebox.showinfo("Wavelength", explanation)

def show_explanation2():
    explanation = """
    - Image Folder
    Click to select the folder where images will be saved.
    The chosen path will appear on the right text box.
    """
    messagebox.showinfo("Image folder", explanation)

def show_explanation3():
    explanation = """
    Open image to define the area to analyze (rectangular region).
    Left click = top-left rectangle, right click = bottom-right rectangle, Esc to save.
    """
    messagebox.showinfo("Select area", explanation)

def show_explanation4():
    explanation = """
    - Spectrum Kinetics
    Real-time transmittance spectra every X seconds.
    Start = begin capture, Stop = finish and retain graph.
    """
    messagebox.showinfo("Spectrum kinetics", explanation)

def show_explanation5():
    explanation = """
    - Single Wavelength Kinetics
    Track transmittance at chosen λ over time.
    One value every X seconds. Start = begin, Stop = end.
    """
    messagebox.showinfo("Single Wavelength Kinetics", explanation)

def show_explanation6():
    explanation = """
    - Save Files
    Enter a name, press Saved → exports PDF and CSV in same folder as script.

    - Reset
    Clears all input fields and internal values to start a new test.

    - Finish
    Closes the interface and ends the program.

    """
    messagebox.showinfo("Save files", explanation)

#configuration of the interface
background="yellowgreen"

frame2=Frame()
frame2.pack(fill="both",expand="True")
frame2.config(bg=background)
frame2.config(bd=35) #frame border width
frame2.config(relief="flat")  #for border, border type

# Crear la interfaz con Tkinter
Label(frame2, text="SPECTROPHOTOMETER", fg="black",bg=background,font=("arial",20)).grid(row=0, column=0, padx=10, pady=10)
Label(frame2, text="Time between images(seconds)", fg="black",bg=background,font=("arial",14)).grid(row=1, column=0, padx=10, pady=10)
Label(frame2, text="Wavelength (nm)", fg="black",bg=background,font=("arial",14)).grid(row=2, column=0, padx=10, pady=10)
Label(frame2, text="SPECTRUM KINETICS", fg="black",bg=background,font=("arial",14)).grid(row=5, column=0, padx=10, pady=10)
Label(frame2, text="SINGLE WAVELENGTH KINETICS", fg="black",bg=background,font=("arial",14)).grid(row=7, column=0, padx=10, pady=10)
Label(frame2, text="SAVE FILES", fg="black",bg=background,font=("arial",14)).grid(row=9, column=0, padx=10, pady=10)
# Botón para salir de la aplicación


arrow = "\u2192"

text_with_arrow = f"Enter data {arrow}"

#Asignar la función de cierre de la ventana
#frame2.protocol("WM_DELETE_WINDOW", on_closing)

button4=Button(frame2, text="Image Folder", fg="white", bg="black",font=("arial",14), command=folder)
button4.grid(row=3,column=0,padx=10, pady=10)

button5=Button(frame2, text=text_with_arrow, fg="white", bg="black",font=("arial",14), command=tiempo)
button5.grid(row=1,column=2,padx=10, pady=10)

button6=tk.Button(frame2, text="Finish", fg="white", bg="black",font=("arial",14), command=terminar)
button6.grid(row=10,column=3, padx=10, pady=10)

button7=tk.Button(frame2, text="Start", fg="white", bg="black",font=("arial",14), command=Start)
button7.grid(row=8,column=0, padx=10, pady=10)

button8=Button(frame2, text=text_with_arrow, fg="white", bg="black",font=("arial",14), command=landa)
button8.grid(row=2,column=2,padx=10, pady=10)

button9=Button(frame2, text="Select area", fg="white", bg="black",font=("arial",14), command=area)
button9.grid(row=4,column=0,padx=10, pady=10)

btn_exit = Button(frame2, text="Stop",fg="white", bg="black",font=("arial",14), command=detener, state=tk.DISABLED)
btn_exit.grid(row=8,column=1, padx=20, pady=20)

button10=tk.Button(frame2, text="Start", fg="white", bg="black",font=("arial",14), command=Start1)
button10.grid(row=6,column=0, padx=10, pady=10)

btn_exit2 = Button(frame2, text="Stop",fg="white", bg="black",font=("arial",14), command=detener1, state=tk.DISABLED)
btn_exit2.grid(row=6,column=1, padx=20, pady=20)

button11=tk.Button(frame2, text="Reset", fg="white", bg="black",font=("arial",14), command=Reset)
button11.grid(row=10,column=2, padx=10, pady=10)

button12=tk.Button(frame2, text="Save file", fg="white", bg="black",font=("arial",14), command=saved)
button12.grid(row=10,column=0, padx=10, pady=10)

#Configuration of all information buttons

button_info = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info.grid(row=1,column=3,sticky="e",padx=0, pady=0)
button_info.bind("<Button-1>", lambda event: show_explanation())

button_info1 = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info1.grid(row=2,column=3,sticky="e",padx=0, pady=0)
button_info1.bind("<Button-1>", lambda event: show_explanation1())

button_info2 = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info2.grid(row=3,column=2,sticky="e",padx=0, pady=0)
button_info2.bind("<Button-1>", lambda event: show_explanation2())

button_info3 = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info3.grid(row=4,column=2,sticky="e",padx=0, pady=0)
button_info3.bind("<Button-1>", lambda event: show_explanation3())

button_info4 = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info4.grid(row=5,column=0,sticky="e",padx=0, pady=0)
button_info4.bind("<Button-1>", lambda event: show_explanation4())

button_info5 = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info5.grid(row=7,column=0,sticky="e",padx=0, pady=0)
button_info5.bind("<Button-1>", lambda event: show_explanation5())

button_info6 = tk.Label(frame2, text="i", fg="black", cursor="hand2")
button_info6.grid(row=9,column=0,sticky="e",padx=0, pady=0)
button_info6.bind("<Button-1>", lambda event: show_explanation6())


example1=StringVar()
example2=StringVar()
example3=StringVar()

landa1=StringVar()
landa2=StringVar()
area1=StringVar()
save1=StringVar()

text_box3=tk.Entry(frame2, textvariable=example1,font=("arial",14),width=10) 
text_box3.grid(row=1,column=1, padx=20, pady=10)

text_box4=tk.Entry(frame2, textvariable=example2,font=("arial",14),width=10) 
text_box4.grid(row=1,column=3, padx=20, pady=10)

text_box6=tk.Entry(frame2, textvariable=landa1,font=("arial",14),width=10) 
text_box6.grid(row=2,column=1, padx=20, pady=10)

text_box7=tk.Entry(frame2, textvariable=landa2,font=("arial",14),width=10) 
text_box7.grid(row=2,column=3, padx=20, pady=10)

text_box5=tk.Entry(frame2, textvariable=example3,font=("arial",14)) 
text_box5.grid(row=3,column=1, padx=10, pady=10)

text_box8=tk.Entry(frame2, textvariable=area1,font=("arial",14)) 
text_box8.grid(row=4,column=1, padx=10, pady=10)

text_box9=tk.Entry(frame2, textvariable=save1,font=("arial",14)) 
text_box9.grid(row=10,column=1, padx=10, pady=10)
# Iniciar el servidor Flask en un hilo para que funcione en segundo plano
#flask_thread = FlaskThread()
#flask_thread.start()



# Ejecutar la interfaz gráfica
raiz.mainloop()