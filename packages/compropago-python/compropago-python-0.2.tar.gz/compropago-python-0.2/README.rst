Compropago en Python
====================

This is the Python library for ComproPago (https://compropago.com/), a Mexican
payment gateway.

Spanish from now on...

Esta es la libreria de Python para Compropago (https://compropago.com/).

ComproPago es una plataforma de pagos en efectivo que ayuda a que personas que
no cuentan con tarjeta de crédito puedan realizar transacciones en tiendas en
línea.

Los clientes finales puedan pagar sus compras de Internet en establecimientos
como 7Eleven, Oxxo, Extra, Soriana, Walmart, Coppel, Farmacia Benavides,
Bodega Aurrera y Farmacias Guadalajara entre otros.


Instalación
-----------

Con ``pip`` se instala así::

    pip install compropago-python

Si usas `zc.buildout <http://www.buildout.org/en/latest/>`_ solo necesitas
añadir ``compropago-python`` a la sección ``eggs``::

    [buildout]
    eggs =
        ...
        compropago-python

Instalación en modo desarrollo
------------------------------

Debes de tener instalado pip y de preferencia virtualenv y virtualenvwrapper.

.. code-block:: bash

    mkvirtualenv ve
    workon ve
    cd compropago-python
    python setupy.py develop

Con esto se instalan las dependencias. Ahora solo necesitas correr las pruebas.

.. code-block:: bash
    nosetests

En Windoge
~~~~~~~~~~

Instala Python. Yo lo instale con chocolatey, pero puedes usar el metodo
que quieras. Chocolatey instaló python en C:\Tools\Python2.

Después de instalar Python hay que instalar pip con `get-pip.py
<https://bootstrap.pypa.io/get-pip.py>`_. [1]_

.. code-block:: msdos
    C:\Tools\Python2\python.exe get-pip.py

Despues puedes instalar virtualenv y crear tu entorno virtual.

.. code-block:: msdos
    C:\Tools\Python2\Scripts\pip.exe install virtualenv
    CD C:\Code\MyProject
    C:\Tools\Python2\Scripts\mkvirtualenv.exe ve
    ve\Scripts\activate.exe

Finalmente:

.. code-block:: msdos
    cd compropago-python
    ..\ve\Scripts\python.exe setup.py develop
    ..\ve\Scripts\nosetests.exe


¿Cómo crear un cargo?
---------------------

Para cualquier operación con el API de Compropago tendrás que usar la llave pública que puedes obtener en el panel de Control de Compropago.

.. code-block:: python
    from compropago import CompropagoAPI, CompropagoCharge
    COMPROPAGO_PUBLIC_API_KEY = '687881193b2423'
    api = CompropagoAPI(COMPROPAGO_PUBLIC_API_KEY)
    c = CompropagoCharge(
        order_id = '1', # De preferencia un numero consecutivo asociado a una orden de compra
        order_price = '10.59', #Compropago solo maneja pesos
        order_name = 'La tiendita de la esquina',
        customer_name = 'Fulano Fernandes',
        customer_email = perengano@perez.com,
        payment_type = 'OXXO'
    )
    r = api.charge(c)

Nota: Hay dos versiones del API: 1.0 y 1.1. Las dos versiones difieren bastante. 
Si Compropago falla diciendo que la llave es invalida, prueba con la otra llave
que te dan el panel de control.

Los tipos de pagos soportados por `payment_type` son::

    OXXO
    SEVEN_ELEVEN
    EXTRA
    CHEDRAUI
    ELEKTRA
    COPPEL
    FARMACIA_BENAVIDES
    FARMACIA_ESQUIVAR


Verificar un cargo existente
----------------------------

Necesitaras el id del pago creado en el paso anterior.

.. code-block:: python
    from compropago impo    rt CompropagoAPI
    COMPROPAGO_PUBLIC_API_KEY = '687881193b2423'
    api = CompropagoAPI(COMPROPAGO_PUBLIC_API_KEY)
    payment_id = '123234' # Viniendo de alguna pa
    res = api.verify_charge(pay_id)
    if res['object'] == 'event' and res['type'] == 'charge.success':
        print "Pagado"

Errores
--------

Código  Descripción

4001    Llave no encontrada
5001    ID de pago no encontrado
5002    Tienda no encontrada
5003    El precio del producto excede el límite por transacción en el establecimiento seleccionado
6001    Hubo un problema con el proveedor de SMS y el mensaje no se envío
6002    Se ha superado el número de envios SMS, máximo 2 mensajes por orden de pago
6003    Compañia celular inválida, soportamos: TELCEL, MOVISTAR, IUSACELL, UNEFON y NEXTEL
6004    Número de celular no válido, probablemente el número contiene menos o más de 10 dígitos


