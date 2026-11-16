import unittest
from unittest.mock import patch
from app import app

class FlaskTests(unittest.TestCase):
    def setUp(self):
        self.client=app.test_client()

    @patch("app.client")
    def test_health(self,mock_client):
        response=self.client.get("/health")
        self.assertEqual(response.status_code,200)

    @patch("app.get_dropdowns",return_value={"states":[],"districts":[],"crops":[],"seasons":[]})
    def test_bad_year(self,_):
        response=self.client.post("/predict",data={"state":"X","district":"Y","season":"Z","crop":"T","year":"bad","area":"1"})
        self.assertEqual(response.status_code,400)
        self.assertIn(b"invalid literal",response.data)

    @patch("app.get_dropdowns",return_value={"states":[],"districts":[],"crops":[],"seasons":[]})
    def test_negative_area(self,_):
        response=self.client.post("/predict",data={"state":"X","district":"Y","season":"Z","crop":"T","year":"2026","area":"-5"})
        self.assertEqual(response.status_code,400)
