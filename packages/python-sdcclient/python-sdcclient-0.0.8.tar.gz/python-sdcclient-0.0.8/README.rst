FIWARE SDC Python Client
================================

This is a client for Saggita SDC API. This API client has been developed in Python_. This client uses
the OpenStack Keystone service for authorization and service endpoint management.

Environment
-----------

**Prerequisites**

- `Python 2.7`__ or newer
- pip_ 6.0 or newer
- Additional libs that are required before installing dependencies: Python Development Tools (python-devel),
zlib-devel, bzip2-devel, openssl-devel, ncurses-devel, sqlite-devel, gcc
- SDC_
- `OpenStack Keystone service`_ v2 (so far, only Keystone v2 is supported for this client)

__ `Python - Downloads`_


**Installation**

All dependencies has been defined in ``requirements.txt``.
To install the last version of this client, download it from the GIT SDC repository (*master* branch)
and install it, using following command:

::

    pip install -e " git+https://github.com/telefonicaid/fiware-sdc.git@master#egg=python-sdcclient&subdirectory=python-sdcclient"


Developed operations
---------------------

Following operations are already implemented:

**ProductAndRelease API Resource**

- Get All ProductAndRelease from SDC catalog


Python API
----------

An example of use of this client is:

::

    from sdcclient.client import SDCClient
    sdc_client = SDCClient(user, password, tenant_id, auth_url, region_name)
    productandrelease_client = sdc_client.getProductAndReleaseResourceClient()

    allproductreleases = productandrelease_client.get_productandrelease()
    assertTrue(response.ok, "ERROR getting productandreleases {}. Response: {}".format(str(allproductreleases.content)))


.. REFERENCES

.. _Python: http://www.python.org/
.. _Python - Downloads: https://www.python.org/downloads/
.. _pip: https://pypi.python.org/pypi/pip
.. _SDC: https://github.com/telefonicaid/fiware-sdc
.. _`OpenStack Keystone service`: http://docs.openstack.org/developer/keystone/
