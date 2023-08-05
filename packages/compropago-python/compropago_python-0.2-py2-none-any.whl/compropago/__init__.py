#coding: utf-8
import json

import requests

from .exceptions import WrongPhoneCompanyError

class CompropagoCharge(object):
    """
        order_id = "SMGCURL1",
        order_price = 10000.0,
        order_name = "SAMSUNG GOLD CURL",
        customer_name = "Alejandra Leyva",
        customer_email = "noreply@compropago.com",
        payment_type = "OXXO"
    """

    def __init__(self, order_id, order_price, order_name, customer_name, customer_email, payment_type):
        self.order_id = order_id
        self.order_price = order_price
        self.order_name = order_name
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.payment_type = payment_type
        # Last update to CP API expects data with these names
        self.product_id = order_id
        self.product_price = order_price
        self.product_name = order_name


    def to_dict(self):
        return {
            'order_id': self.order_id,
            'order_price': self.order_price,
            'order_name': self.order_name,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'payment_type': self.payment_type,
            #Compatibility for new API changes (Jun 16, 2015)
            'product_id': self.product_id,
            'product_price': self.product_price,
            'product_name': self.product_name,
        }


class CompropagoAPI(object):
    errores = {
        4001: u'Llave no encontrada',
        5001: u'ID de pago no encontrado',
        5002: u'Tienda no encontrada',
        5003: u'El precio del producto excede el límite por transacción en el establecimiento seleccionado',
        6001: u'Hubo un problema con el proveedor de SMS y el mensaje no se envío',
        6002: u'Se ha superado el número de envios SMS, máximo 2 mensajes por orden de pago',
        6003: u'Compañia celular inválida, soportamos: TELCEL, MOVISTAR, IUSACELL, UNEFON y NEXTEL',
        6004: u'Número de celular no válido, probablemente el número contiene menos o más de 10 dígitos',
    }

    def __init__(self, api_key, url_base='https://api.compropago.com/v1'):
        self.api_key = api_key
        self.url_base = url_base

    @property
    def auth(self):
        return (self.api_key, '')

    @property
    def headers(self):
        return {
            'Accept': 'application/compropago',
            'Content-Type': 'application/json',
            'User-Agent': 'Django LFS - http://www.getlfs.com/'
        }

    def charge(self, charge):
        if not isinstance(charge, CompropagoCharge):
            raise TypeError('%s no es una instancia de CompropagoCharge.' % str(charge))
        return requests.post(
            '/'.join((self.url_base, 'charges')),
            headers = self.headers,
            json = charge.to_dict(),
            auth = self.auth
        ).json()

    def verify_charge(self, payment_id):
        return requests.get(
            '/'.join((self.url_base, 'charges', payment_id)),
            auth = self.auth,
            headers = self.headers
        ).json()

    def send_sms(self, payment_id, phone, company):
        """
        Ofrece a tus usuarios la posibilidad de recibir las instrucciones de pago
        directo en su telefono celular. Los unicos campos requeridos son el numero
        de celular y su compania telefonica.
        """
        if company.upper() not in ('TELCEL' 'MOVISTAR' 'IUSACELL' 'NEXTEL'):
            raise WrongPhoneCompanyError(
                'Las unicas companias soportadas son TELCEL, IUSACELL y MOVISTAR y NEXTEL'
            )
        payload = json.dumps({'customer_phone': phone, 'customer_company_phone': company})
        return requests.post(
            '/'.join((self.url_base, 'charges', payment_id, 'sms')),
            data = payload,
            auth = self.auth,
            headers = self.headers
        ).json()
