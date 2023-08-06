EBS Gateway
============


**EBS Payment Gateway** is a Python app to integrate EBS payment gateway with a Django Project.

Documentation
-------------

Documentation is available.

Development
-----------

Source code is available at https://bitbucket.org/redpandas/ebs_gateway_python.

To install in a project do a `` pip install ebs_payment ``

You will need 3 configs in your settings

``
SUBMIT_URL = 'https://secure.ebs.in/pg/ma/payment/request'  # The Submit URL
SECRET = '' # The private key
HASH_ALGORITHM = '' # The hashing algorithm. SHA1, SHA512 and MD5 are supported.

``

Without these 3 configs the app won't work.

License
-------

MIT: http://opensource.org/licenses/MIT
