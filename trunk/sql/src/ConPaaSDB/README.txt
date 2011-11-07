ConPaaSDB
=========

Working env
-----------

You have to install dependencies first.

    pip install -r requirements.txt

Running tests
-------------

Unit
++++

nosetests -v -s -w src/conpaasdb/tests/unit

Functional
++++++++++

python src/conpaasdb/tests/remote/run.py -c src/conpaasdb/tests/remote/remote_tests.conf
    
