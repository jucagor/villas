import serial
from gpiozero import LED
import time
import sqlite3
import datetime #Libreria para funciones relacionadas con tiempo (sleep)

breset= LED(17)
breset.on()
Leer = False
Apertura = True         #variable para bloquear o cerrar definitivamente el torniquete
class Lectura:
    def __init__(self,dato):
        self.indicador = dato[9]
        self.UID = dato[22:33]
        print(self.UID)
    
    def informacionDB(self):
        global Leer
        conn= sqlite3.connect(rutaBD)
        #consulto apartamento de la tarjeta leida
        cursor = conn.cursor()
        query = 'SELECT * FROM Usuarios where Codigo = ("{}")'.format(LecturaActual.UID)
        self.Registro = cursor.execute(query).fetchone()
        if self.Registro is None:
            self.Invalido=True
            print('tarjeta no se encuentra en la Base de Datos')
            Leer=False
            arduino.write(str.encode('N'))           
            return
        self.Apto=self.Registro[0]
        self.PasTotal=self.Registro[2]
        self.PasDispon=self.Registro[3]
        self.Bloqueada=self.Registro[4]
        self.Master=self.Registro[5]
        self.MasterApertura=self.Registro[6]
        self.UsoTotal=self.Registro[8]
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
        query += ' WHERE Codigo = "{}"'.format(LecturaActual.UID)
        conn= sqlite3.connect(rutaBD)
        cursor = conn.cursor()
        registro=cursor.execute(query)
        conn.commit()

    def GuardarIngreso(self):
        hora=datetime.datetime.now()
        query = 'UPDATE Usuarios SET UltimoUso="{}"'.format((str(hora)[0:19]))
        query += ' WHERE Codigo = "{}"'.format(LecturaActual.UID)
        if self.UsoTotal ==None:
            query2 = 'UPDATE Usuarios SET UsoTotal="{}"'.format(1)
            query2 += ' WHERE Codigo = "{}"'.format(LecturaActual.UID)
        else:
            query2 = 'UPDATE Usuarios SET UsoTotal="{}"'.format((self.UsoTotal+1))
            query2 += ' WHERE Codigo = "{}"'.format(LecturaActual.UID)
        conn= sqlite3.connect(rutaBD)
        cursor = conn.cursor()
        registro=cursor.execute(query)
        registro2=cursor.execute(query2)
        conn.commit()        
        conn.close()
conectado=False
while conectado==False:
    try:    
        arduino = serial.Serial('/dev/ttyACM0',baudrate=9600)
        print("arduino en puerto ttyACM0")
        conectado=True
    except:
        try:
            arduino = serial.Serial('/dev/ttyACM1',baudrate=9600)
            print("arduino en puerto ttyACM1")
            conectado=True
        except:
            print("placa arduino no disponible")
            time.sleep(1)
    
rutaBD= '/home/pi/Desktop/produccion/base_de_datos_usuarios.db'
data=0
while True:
    try:
        data= arduino.readline()[:-2]
    except:
        print("un error ha ocurrido")
        time.sleep(2)
        try:    
            arduino = serial.Serial('/dev/ttyACM0',baudrate=9600)
            print("arduino en puerto ttyACM0")
        except:
            try:
                arduino = serial.Serial('/dev/ttyACM1',baudrate=9600)
                print("arduino en puerto ttyACM1")
            except:
                print("placa arduino no disponible")
    
    #data = arduino.read(40)
    if data:
        data=str(data)
        if (data.find('Card UID') != -1):       
            #print (data)
            LecturaActual=Lectura(data)                         #Se crea una instancia de la clase lectura con los datos de la lectura
            Leer=True
            print('leyendo')
            print('')
            LecturaActual.informacionDB()
    
    while Leer:
        if LecturaActual.MasterApertura==1:
            if Apertura:
                Apertura=False
            else:
                Apertura=True
        if Apertura and not LecturaActual.Bloqueada :
            if LecturaActual.indicador == '0': #se compara la entrada
                if LecturaActual.Master==1:
                    print ('Entrando Master...')
                    arduino.write(str.encode('E'))
                    Leer=False
                    break
                if LecturaActual.PasDispon > 0 and LecturaActual.PasDispon <= LecturaActual.PasTotal:
                    print('Entrando...')
                    arduino.write(str.encode('E'))
                    LecturaActual.PasDispon = LecturaActual.PasDispon-1
                    LecturaActual.GuardarIngreso()
                    print('nuevos pases disponibles', LecturaActual.PasDispon)
                else:
                    print('no puede entrar, pases no disponibles')
                    arduino.write(str.encode('F'))
            else:
                if LecturaActual.Master==1:
                    print('Saliendo Master...')
                    arduino.write(str.encode('S'))
                    Leer=False
                    break
                if LecturaActual.PasDispon >= 0 and LecturaActual.PasDispon < LecturaActual.PasTotal:
                    print('Saliendo...')
                    arduino.write(str.encode('S'))
                    LecturaActual.PasDispon = LecturaActual.PasDispon+1
                    print('nuevos pases disponibles', LecturaActual.PasDispon)
                else:
                    print('no puede Salir, pases no disponibles')
                    arduino.write(str.encode('F'))
            LecturaActual.GuardarDB()
            Leer=False
            print(datetime.datetime.now())
            #breset.off()
            #time.sleep(0.1)
            #breset.on()
        else:
            print('Torniquete Bloqueado por Apertura o tarjeta Bloqueada')
            arduino.write(str.encode('A'))
            Leer=False
            print(datetime.datetime.now())
    
            
            
            