import unittest
from app import *


class TestAppV1(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_v1_24(self):
        response = self.app.get('/servicio/v1/prediccion/24horas/')
        self.assertEqual(response.status_code, 200)

    def test_v1_48(self):
        response = self.app.get('/servicio/v1/prediccion/48horas/')
        self.assertEqual(response.status_code, 200)

    def test_v1_72(self):
        response = self.app.get('/servicio/v1/prediccion/72horas/')
        self.assertEqual(response.status_code, 200)
