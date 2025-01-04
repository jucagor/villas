import unittest
from unittest.mock import patch, Mock, MagicMock
from start import Torniquete, TipoRespuesta


class TorniqueteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.lectura_entrada = "Reader 0: Card UID: 89 7A 50 B8".encode()
        self.lectura_salida = "Reader 1: Card UID: 89 7A 50 B8".encode()
        self.db_path = "base_de_datos_usuarios.db"
        self.db_query = [
            "97202",
            "AA BB CC 11",
            "4",
            "4",
            "0",
            "0",
            "0",
            "2024-08-06 15:06:39",
            "64",
        ]

    @patch("serial.Serial")
    def test_lectura_arduino_exitoso(self, mock_serial):
        test_torniquete = Torniquete()
        test_torniquete.arduino.readline = MagicMock(
            return_value=self.lectura_entrada)
        mock_serial.assert_called()
        test_torniquete.leer_tarjeta()
        self.assertEqual(test_torniquete.leer_tarjeta(), True)

    @patch("serial.Serial")
    def test_lectura_DB_exitoso(self, mock_serial):
        test_torniquete = Torniquete()
        test_torniquete.arduino.readline = MagicMock(
            return_value=self.lectura_entrada)
        test_torniquete.leer_tarjeta()
        respuesta = test_torniquete.procesar_lectura(self.db_path)
        self.assertEqual(respuesta, TipoRespuesta.INGRESO)

    @patch("serial.Serial")
    def test_salida_no_disponible(self, mock_serial):
        test_torniquete = Torniquete()
        test_torniquete.arduino.readline = MagicMock(
            return_value=self.lectura_salida)
        test_torniquete.leer_tarjeta()
        respuesta = test_torniquete.procesar_lectura(self.db_path)
        self.assertEqual(respuesta, TipoRespuesta.SALIDA_NO_DISPONIBLE)

    @patch("serial.Serial")
    def test_ingreso_y_descontar_pase_exitoso(self, mock_serial):
        test_torniquete = Torniquete()
        test_torniquete.arduino.readline = MagicMock(
            return_value=self.lectura_entrada)
        test_torniquete.leer_tarjeta()
        respuesta = test_torniquete.procesar_lectura(self.db_path)
        self.assertEqual(respuesta, TipoRespuesta.INGRESO)
        test_torniquete.PasDispon = test_torniquete.PasDispon - 1
        test_torniquete.update_ingreso(self.db_path)
        test_torniquete.update_pases(self.db_path)
        respuesta = test_torniquete.procesar_lectura(self.db_path)
        self.assertEqual(test_torniquete.PasDispon, 3)
        test_torniquete.PasDispon = test_torniquete.PasDispon + 1
        test_torniquete.update_pases(self.db_path)

    @patch("serial.Serial")
    def test_salida_y_adicionar_pase_exitoso(self, mock_serial):
        test_torniquete = Torniquete()
        test_torniquete.arduino.readline = MagicMock(
            return_value=self.lectura_entrada)
        test_torniquete.leer_tarjeta()
        respuesta = test_torniquete.procesar_lectura(self.db_path)
        self.assertEqual(respuesta, TipoRespuesta.INGRESO)

        test_torniquete.PasDispon = test_torniquete.PasDispon - 1
        test_torniquete.update_pases(self.db_path)

        test_torniquete.PasDispon = test_torniquete.PasDispon + 1
        test_torniquete.update_ingreso(self.db_path)
        test_torniquete.update_pases(self.db_path)
        self.assertEqual(test_torniquete.PasDispon, 4)
