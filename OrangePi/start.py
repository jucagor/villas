from __future__ import annotations
from enum import Enum

import os
import sqlite3
import datetime
import time
import serial


class TipoRespuesta(Enum):
    """Enum que representa los diferentes tipos de respuesta del torniquete a una lectura
    y su respectivo codigo serial de respuesta para el Arduino

    """

    ENTRADA_MASTER = "EM"
    SALIDA_MASTER = "SM"
    INGRESO = "E"
    ENTRADA_NO_DISPONIBLE = "EF"
    SALIDA = "S"
    SALIDA_NO_DISPONIBLE = "SF"
    UID_NO_IDENTIFICADO = "N"
    UID_BLOQUEADO = "A"


class Torniquete:
    arduino: serial.Serial

    def __init__(self) -> None:
        self.disponible: bool = True  # Variable que bloque el torniquete de todo
        self.data: str = ""  # Lectura sin procesar del arduino

        self.id_sensor: int = (
            7  # Posicion del string que indica el sensor que realiza la lectura, 0 entrada 1 salida        #
        )

        self._conectar_con_arduino()

    def _conectar_con_arduino(self):

        conexion_arduino = False
        while not conexion_arduino:
            try:
                self.arduino = serial.Serial("/dev/ttyACM0", baudrate=9600)
                print("arduino en puerto ttyACM0")
                conexion_arduino = True
            except BaseException:
                try:
                    self.arduino = serial.Serial("/dev/ttyACM1", baudrate=9600)
                    print("arduino en puerto ttyACM1")
                    conexion_arduino = True
                except BaseException:
                    print("placa arduino no disponible")
                    time.sleep(1)

    def leer_tarjeta(self) -> bool:
        """Lee el puerto serial y verifica si hay una lectura valida del sensor

        Returns:
            bool: Si se ha realizado una lectura valida por parte de algun sensor
        """
        try:
            raw_data = self.arduino.readline()  # TODO Pendiente por verificar
        except BaseException:
            print("un error ha ocurrido al leer la tarjeta")
        if (
            raw_data and raw_data.decode().find("Card UID") != -1
        ):  # Si llego algo desde el arduino y fue una lectura de un sensor
            self.data = raw_data.decode()
            print(
                "leyendo sensor {value} con UID: {uid}".format(
                    value=["Entrada", "Salida"][int(self.data[self.id_sensor])],
                    uid=self.data[20:31],
                )
            )
            print("")
            return True
        return False

    def procesar_lectura(self, db_path) -> TipoRespuesta:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        self.uid = self.data[20:31]
        query = 'SELECT * FROM Usuarios where Codigo = ("{}")'.format(self.uid)
        self.Registro = cursor.execute(query).fetchone()
        if self.Registro is None:
            print("tarjeta no se encuentra en la Base de Datos")
            return TipoRespuesta.UID_NO_IDENTIFICADO
        conn.close()
        Apto = self.Registro[0]
        PasTotal = self.Registro[2]
        self.PasDispon = self.Registro[3]
        Bloqueada = self.Registro[4]
        Master = self.Registro[5]
        MasterApertura = self.Registro[6]
        self.UsoTotal = self.Registro[8]
        print("apartamento numero:", Apto)
        print("pases totales tarjeta:", PasTotal)
        print("pases disponibles:", self.PasDispon)
        if Bloqueada == 1:
            return TipoRespuesta.UID_BLOQUEADO

        if Master == 1:
            print("Si es tarjeta maestra")

        if self.data[self.id_sensor] == "0":  # Entrada
            if Master == 1:
                return TipoRespuesta.ENTRADA_MASTER
            if self.PasDispon > 0 and self.PasDispon <= PasTotal:
                return TipoRespuesta.INGRESO
            else:
                return TipoRespuesta.ENTRADA_NO_DISPONIBLE
        else:
            if Master == 1:
                return TipoRespuesta.SALIDA_MASTER
            if self.PasDispon >= 0 and self.PasDispon < PasTotal:
                return TipoRespuesta.SALIDA
            else:
                return TipoRespuesta.SALIDA_NO_DISPONIBLE

    def update_ingreso(self, db_path):
        hora = datetime.datetime.now()
        query = 'UPDATE Usuarios SET UltimoUso="{}"'.format((str(hora)[0:19]))
        query += ' WHERE Codigo = "{}"'.format(self.uid)
        if self.UsoTotal is None:
            query2 = 'UPDATE Usuarios SET UsoTotal="{}"'.format(1)
            query2 += ' WHERE Codigo = "{}"'.format(self.uid)
        else:
            print('++++++++++++++++')
            print(self.UsoTotal)
            query2 = 'UPDATE Usuarios SET UsoTotal="{}"'.format(
                (self.UsoTotal + 1))
            query2 += ' WHERE Codigo = "{}"'.format(self.uid)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        registro = cursor.execute(query)
        registro2 = cursor.execute(query2)
        conn.commit()
        conn.close()

    def update_pases(self, db_path):
        query = 'UPDATE Usuarios SET PasDisponibles="{}"'.format(
            self.PasDispon)
        query += ' WHERE Codigo = "{}"'.format(self.uid)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        registro = cursor.execute(query)
        conn.commit()
        conn.close()

    def verificar_conexion(self):
        pass


if __name__ == "__main__":

    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    datastore_path = basedir + "/base_de_datos_usuarios.db"
    print(
        f"Base de datos en: {datastore_path}".format(
            datastore_path=datastore_path))
    if not os.path.exists(datastore_path):
        print("base de datos no existe")
        try:
            raise SystemExit
        except BaseException:
            print("Finalizar el programa a trave de la excepcion no es posible")

    torniquete = Torniquete()
    while True:
        if torniquete.leer_tarjeta():
            respuesta = torniquete.procesar_lectura(datastore_path)

            if respuesta == TipoRespuesta.UID_NO_IDENTIFICADO:
                print("Tarjeta no se encuentra en la base de datos")
                torniquete.arduino.write(
                    str.encode(TipoRespuesta.UID_NO_IDENTIFICADO.value)
                )

            if respuesta == TipoRespuesta.UID_BLOQUEADO:
                print("Tarjeta Se encuentra Bloqueada")
                torniquete.arduino.write(str.encode(
                    TipoRespuesta.UID_BLOQUEADO.value))

            if respuesta == TipoRespuesta.ENTRADA_NO_DISPONIBLE:
                print("No puede entrar, pases no disponibles")
                torniquete.arduino.write(str.encode('F'))  # str.encode(TipoRespuesta.ENTRADA_NO_DISPONIBLE.value)

            if respuesta == TipoRespuesta.SALIDA_NO_DISPONIBLE:
                print("No puede salir, pases no disponibles")
                torniquete.arduino.write(str.encode('F'))  # str.encode(TipoRespuesta.SALIDA_NO_DISPONIBLE.value)

            if respuesta == TipoRespuesta.ENTRADA_MASTER:
                print("Entrando Master")
                torniquete.arduino.write(
                    str.encode(TipoRespuesta.INGRESO.value))

            if respuesta == TipoRespuesta.SALIDA_MASTER:
                print("Salida Master")
                torniquete.arduino.write(
                    str.encode(TipoRespuesta.SALIDA.value))

            if respuesta == TipoRespuesta.INGRESO:
                torniquete.PasDispon = torniquete.PasDispon - 1
                torniquete.update_ingreso(datastore_path)
                torniquete.update_pases(datastore_path)
                print("nuevos pases disponibles", torniquete.PasDispon)
                torniquete.arduino.write(
                    str.encode(TipoRespuesta.INGRESO.value))

            if respuesta == TipoRespuesta.SALIDA:
                torniquete.PasDispon = torniquete.PasDispon + 1
                torniquete.update_pases(datastore_path)
                print("nuevos pases disponibles", torniquete.PasDispon)
                torniquete.arduino.write(
                    str.encode(TipoRespuesta.SALIDA.value))

            print(datetime.datetime.now())
