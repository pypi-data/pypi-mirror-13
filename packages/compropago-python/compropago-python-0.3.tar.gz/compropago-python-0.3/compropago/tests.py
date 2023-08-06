#coding: utf-8
import unittest
import requests
import responses
from compropago import CompropagoAPI, Charge

class APITestCase(unittest.TestCase):
    def test_api_constructor(self):
        api = CompropagoAPI('My API Key')
        assert(api.api_key == 'My API Key')
        assert(api.url_base == 'https://api.compropago.com/v2')


class CompropagoTestCharge(unittest.TestCase):
    def test_cargo_object(self):
        c = Charge(
            product_price = 10000.0,
            product_name = "SAMSUNG GOLD CURL",
            product_id = "SMGCURL1",
            image_url = "https =//test.amazon.com/5f4373",
            customer_name = "Alejandra Leyva",
            customer_email = "noreply@compropago.com",
            payment_type = "OXXO"
        )
        assert isinstance(c.to_dict(), dict)

    @responses.activate
    def test_create_charge(self):
        API_KEY = '687881193b2423'
        api = CompropagoAPI(API_KEY)
        responses.add(
            responses.POST,
            'https://api.compropago.com/v2/charges',
            body = """
            {
             "payment_id": "c0991dd38-e408-4f27",
             "short_payment_id": "00927c",
             "payment_status": "PENDING",
             "creation_date": "2013-09-30T04:46:04Z",
             "expiration_date": "2013-10-01T04:46:04Z",
             "product_information": {
               "product_id": "IB18S",
               "product_name": "Samsung Galaxy Gold",
               "product_price": 10000.0,
              }
             "payment_instructions":{
               "description": "Para que el pago sea valido debes pagar ...",
               "step_1": "Ir a la caja OXXO ...",
               "step_2": "Solicitar deposito ...",
               "step_3": "Deposite la cantidad ...",
               "note_extra_comition": "Las tiendas OXXO 
                 cobran en caja una comisión de 7 pesos",
               "note_expiration_date": "Orden válida 
                 antes de 01/10/2013",
               "note_confirmation": "Tu pago será 
                 confirmado a través de SMS y email",
              }
            }
            """,
            content_type='application/json'
        )
        c = Charge(
            product_price = 10000.0,
            product_name = "SAMSUNG GOLD CURL",
            product_id = "SMGCURL1",
            image_url = "https =//test.amazon.com/5f4373",
            customer_name = "Alejandra Leyva",
            customer_email = "noreply@compropago.com",
            payment_type = "OXXO"
        )
        resp = api.charge(c)
        assert len(responses.calls) == 1

    @responses.activate
    def test_verify_charge(self):
        from compropago import CompropagoAPI
        API_KEY = '687881193b2423'
        api = CompropagoAPI(API_KEY)
        responses.add(
            responses.GET,
            'https://api.compropago.com/v2/charges/c90870de-55a2-4b50-bd6b-9c7887787b35',
            body = """
              {
                "type":"charge.pending",
                "object":"event",
                "data": {
                   "object": {
                    "id": "fe92a1a5-abec-49e3-877c-5024c1464dc3",
                    "object": "charge",
                    "created_at": "2013-12-09T18:59:28.048Z",
                    "paid": true,
                    "amount": "150.00",
                    "currency": "mxn",
                    "refunded": false,
                    "fee": "7.50",
                    "fee_details": {
                      "amount": "7.50",
                      "currency": "mxn",
                      "type": "compropago_fee",
                      "description": "Honorarios de ComproPago",
                      "application": null,
                      "amount_refunded": 0,
                    }
                    "payment_details": {
                      "object": "cash",
                      "store": "OXXO",
                      "country": "MX",
                      "product_id": "SMGCURL1",
                      "product_price": "150.00",
                      "product_name": "SAMSUNG GOLD CURL",
                      "image_url": "https://test.amazon.com/5f4373",
                      "success_url": "",
                      "customer_name": "Alejandra Leyva",
                      "customer_email": "noreply@compropago.com",
                      "customer_phone": "2221515801",
                    }
                    "captured": true,
                    "failure_message": null,
                    "failure_code": null,
                    "amount_refunded": 0,
                    "description": "Estado del pago - ComproPago",
                    "dispute": null,
                  }
                }
              }
              """)
        resp = api.verify_charge('c90870de-55a2-4b50-bd6b-9c7887787b35')
        assert len(responses.calls) == 1


class TestSMS(unittest.TestCase):
    @responses.activate
    def test_send_sms(self):
        API_KEY = '687881193b2423'
        api = CompropagoAPI(API_KEY)
        responses.add(
            responses.POST,
            'https://api.compropago.com/v2/charges/f4172ff7-9125-4206-99c7-151480b036ad/sms',
            body = """{
               "type": "charge_sms.success",
               "object": "event",
               "payment": {
                 "id": "f4172ff7-9125-4206-99c7-151480",
                 "short_id": "04c651",
                }
              }""")
        resp = api.send_sms(
            payment_id = 'f4172ff7-9125-4206-99c7-151480b036ad',
            phone = '2221515805',
            company = 'TELCEL'
        )
        assert len(responses.calls) == 1
