from flask import Flask, flash, request, redirect, render_template, session
import time
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
error=None
Logeo=False
#rutaBD= 'C:/Users/jcgr1/Desktop/base_de_datos_usuarios.db'
rutaBD= 'C:/Users/camilo/Desktop/base_de_datos_usuarios_2.db'
class datosdb:
    def __init__(self):
        self.data=[]
        self.apt=[]
        self.alldata=[]
        self.allapto=[]


def leerdb():
    conn= sqlite3.connect(rutaBD)
    cursor = conn.cursor()
    query1 = 'SELECT * FROM Usuarios where PasDisponibles < ("5")'
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
    print(str(datos.apt[2]))
    return datos

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global error
    global Logeo
    if request.method == 'POST':
        print(request.form)
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'secret':
            error = 'Contraseña invalida'
        else:
            Logeo = True
            return redirect('/monitoreo')
    return render_template('login.html', error=error)

@app.route('/monitoreo', methods=['GET'])
def monitoreo():
    datos=leerdb()
    if Logeo:
        return render_template('monitoreo.html', datos=datos, Logeo=Logeo)
    else:
        global error
        error= 'debe autenticarse'
        return redirect('/login')

@app.route('/usuarios')
def usuarios():
    datos=leerdb()
    if Logeo:
        return render_template('visualizacionusuarios.html', datos=datos, Logeo=Logeo)
    else:
        global error
        error= 'debe autenticarse'
        return redirect('/login')
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port='88')
