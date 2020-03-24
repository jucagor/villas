from flask import Flask, flash, request, redirect, render_template, session
import datetime
import sqlite3

rutaBD= 'C:/Users/camilo/villas/base_de_datos_usuarios.db'

class Lectura:
    def __init__(self,dato):
        self.numeroapto = dato

    def informacionDB(self):
        conn= sqlite3.connect(rutaBD)
        #consulto apartamento de la tarjeta leida
        cursor = conn.cursor()
        query = 'SELECT * FROM Usuarios where ID = ("{}")'.format(LecturaActual.numeroapto)
        self.Registro = cursor.execute(query).fetchone()
        if self.Registro is None:
            self.Invalido=True
            print('tarjeta no se encuentra en la Base de Datos')       
            return
        self.Apto=self.Registro[0]
        self.PasTotal=self.Registro[2]
        self.PasDispon=self.Registro[3]
        self.Bloqueada=self.Registro[4]
        self.Master=self.Registro[5]
        self.MasterApertura=self.Registro[6]
        self.UltimoUso=self.Registro[7]
        self.UsoTotal=self.Registro[8]
        print('USO TOTAL:',self.UsoTotal)
        print('ULTIMO USO:',self.UltimoUso)
        print('apartamento numero:',self.Apto)
        print('pases totales tarjeta:',self.PasTotal)
        print('pases disponibles:',self.PasDispon)
        if self.Bloqueada==0:
            print('la tarjeta NO esta bloqueada')
        else:
            print('la tarjeta esta bloqueada')
            
        if self.Master==0:
            print('No es tarjeta maestra')
        else:
            print('Si es tarjeta maestra')
        if self.MasterApertura==0:
            print('NO es Master de Apertura')
        else:
            print('SI es Master de Apertura')
        conn.close()

    def GuardarDB(self):
        query = 'UPDATE Usuarios SET PasDisponibles="{}"'.format(LecturaActual.PasDispon)
        query += ' WHERE ID = "{}"'.format(LecturaActual.numeroapto)
        conn= sqlite3.connect(rutaBD)
        cursor = conn.cursor()
        registro=cursor.execute(query)
        conn.commit()
    
    def GuardarIngreso(self):
        hora=datetime.datetime.now()
        query = 'UPDATE Usuarios SET UltimoUso="{}"'.format((str(hora)[0:19]))
        query += ' WHERE ID = "{}"'.format(LecturaActual.numeroapto)
        if self.UsoTotal ==None:
            query2 = 'UPDATE Usuarios SET UsoTotal="{}"'.format(1)
            query2 += ' WHERE ID = "{}"'.format(LecturaActual.numeroapto)
        else:
            query2 = 'UPDATE Usuarios SET UsoTotal="{}"'.format((self.UsoTotal+1))
            query2 += ' WHERE ID = "{}"'.format(LecturaActual.numeroapto)
        conn= sqlite3.connect(rutaBD)
        cursor = conn.cursor()
        registro1=cursor.execute(query)
        registro2=cursor.execute(query2)
        conn.commit()   
        conn.close()




if __name__ == '__main__':
    while True:

        data=int(input("ingrese numero de apartamento: "))
        LecturaActual=Lectura(data)
        LecturaActual.informacionDB()
        accion=input("desea simular un ingreso o una salida? (Escriba porfavor las palabras: 'ingreso' 'salida') ")
        if accion == ('ingreso'):
            print(LecturaActual.numeroapto," Entrando")
            LecturaActual.PasDispon = LecturaActual.PasDispon-1
            LecturaActual.GuardarIngreso()
            LecturaActual.GuardarDB()
        elif accion ==('salida'):
            print(LecturaActual.numeroapto," Saliendo")
            LecturaActual.PasDispon = LecturaActual.PasDispon+1
            LecturaActual.GuardarDB()
        else:
            print("ingrese un comando valido")
            pass

    