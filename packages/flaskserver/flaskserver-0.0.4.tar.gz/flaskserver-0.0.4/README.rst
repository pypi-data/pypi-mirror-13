Module flaskserver
==================

simple static web server

Installation
------------

::

    pip install flaskserver
    
Or

::

    git clone https://github.com/fraoustin/flaskserver.git
    cd flaskserver
    python setup.py install
        
Usage
-----

::

    flask

use personnal flask.conf

::

    import os

    INDEX = True
    CORS = True
    COLOR = True
    DIRECTORY_INDEX = 'index.html'
    PORT = 5001
    HOST = '0.0.0.0'
    PATH_HTML = os.getcwd()
