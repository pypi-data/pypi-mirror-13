lambda-project-creator
===============

Easily and quickly command line utility creating Lambda Project for lambda-uploader(https://pypi.python.org/pypi/lambda-uploader).

Installation
~~~~~~~~~~~~

The latest release of lambda-project-creator can be installed via pip:

::

    pip install lambda-project-creator

An alternative install method would be manually installing it leveraging
``setup.py``:

::

    git clone https://github.com/cloudfish7/lambda-project-creator
    cd lambda-project-creator
    python setup.py install


Command Line Usage
~~~~~~~~~~~~~~~~~~

To create Lambda Project simply, run following command

.. code:: shell

    lambda-project-creator -p sampleprj

Get created following file and directory. Also get installed lambda-uploader.

.. code:: shell

   sampleprj
    ├── .venv_sampleprj
    ├── lambda.json
    ├── requirement.txt
    └── lambda.py


