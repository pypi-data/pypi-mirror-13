=========
Tipsa API
=========

This package create packages to send using TIPSA API.

License
-------

The package is released under the New BSD license.

Example of use
--------------

.. code-block:: python

    from tipsa import api

    tipsa_api = api.TipsaAPI('agency_code', 'client_code', 'client_password')

    tipsa_api.login() # Web service login

    result = tipsa_api.create({
        'service_code': 'service_code',
        'destination_name': 'destination_name',
        'destination_address': 'destination_address',
        'destination_postal_code': 'destination_postal_code',
        'destination_city': 'destination_city'
    }) # Create a shipping

    print result['albaran']
    print result['guid']
    print result['url'] # Url to check status