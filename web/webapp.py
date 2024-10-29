# -*- coding: utf-8 -*-
from flask import Flask, flash, request, redirect, render_template, session
import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
error=None
Logeo=False
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rutaBD = basedir + "/base_de_datos_usuarios.db"
class datosdb:
    def __init__(self):
        self.data=[]
        self.apt=[]
        self.alldata=[]
        self.allapto=[]


def leerdb():
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    query1 = 'SELECT * FROM Usuarios where PasDisponibles < ("4")'
    query2 = 'SELECT * FROM Usuarios'
    datos=datosdb
    datos.data= cursor.execute(query1).fetchall()
    datos.alldata= cursor.execute(query2).fetchall()
    lista=[]
    for i in range(len(datos.data)):
        lista.append(str(datos.data[i][0]))
    conn.close()
    datos.apt=lista
    lista2=[]
    for i in range(len(datos.alldata)):
        lista2.append(str(datos.alldata[i][0]))
    conn.close()
    datos.allapt=lista2
    return datos

def bloqueouser(apto):
    query = 'UPDATE Usuarios SET Bloqueo=1'
    query += ' WHERE ID = "{}"'.format(apto)
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    registro=cursor.execute(query)
    conn.commit()
    conn.close()

def desbloqueouser(apto):
    query = 'UPDATE Usuarios SET Bloqueo=0'
    query += ' WHERE ID = "{}"'.format(apto)
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    registro=cursor.execute(query)
    conn.commit()
    conn.close()
    
def reset_all_pases(apto):
    query = 'UPDATE Usuarios SET PasDisponibles = 4'
    query += ' WHERE PasDisponibles < 4'
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    registro=cursor.execute(query)
    conn.commit()
    conn.close()

def restartpass(apto):
    query = 'UPDATE Usuarios SET PasDisponibles=4'
    query += ' WHERE ID = "{}"'.format(apto)
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    registro=cursor.execute(query)
    conn.commit()
    conn.close() 

def Guardartime(apto):
    hora=datetime.datetime.now()
    query = 'UPDATE Usuarios SET UltimoUso="{}"'.format((str(hora)[0:19]))
    query += ' WHERE ID = "{}"'.format(apto)
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    registro=cursor.execute(query)
    conn.commit()        
    conn.close()


@app.route('/')
def index():
    global Logeo
    Logeo = False
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global error
    global Logeo
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != '12345villas':
            error = 'contrasena invalida'
        else:
            Logeo = True
            error=None
            return redirect('/monitoreo')
    return render_template('login.html', error=error)

@app.route('/monitoreo', methods=['GET'])
def monitoreo():
    datos=leerdb()
    if Logeo:
        return render_template('tablamonitoreo.html', datos=datos)
    else:
        global error
        error= 'debe autenticarse'
        return redirect('/login')

@app.route('/usuarios', methods=['GET','POST'])
def usuarios():
    if Logeo:
        if request.method == 'POST':
            try: 
                if request.form['bloqueo']:
                    bloqueouser(request.form['bloqueo'])
            except:
                try:             
                    if request.form['desbloqueo']:
                        desbloqueouser(request.form['desbloqueo'])
                except:
                    if request.form['restartpass']:
                        restartpass(request.form['restartpass'])
        datos=leerdb()
        return render_template('tablausuarios.html', datos=datos, Logeo=Logeo)
    else:
        global error
        error= 'debe autenticarse'
        return redirect('/login')


@app.route('/configuracion', methods=['GET','POST'])
def configurar():
    if Logeo:
        if request.method == 'POST':
            try:
                if request.form['block']:
                    # Bloquear el torniquete
                    pass
            except:
                try:
                    if request.form['desbloqueo']:
                        desbloqueouser(request.form['desbloqueo'])
                except:
                    if request.form['restartallpass']:
                        # Resetear todas las tarjetas
                        pass
        datos=leerdb()
        return render_template('configuracion.html', datos=datos, Logeo=Logeo)
    else:
        global error
        error= 'debe autenticarse'
        return redirect('/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port='80')
