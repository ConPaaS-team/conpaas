ConPaaSSQL Manager GUI
----------------------

Install
-------

::

    apt-get install python-setuptools python-dev python-pycurl -y

    easy_install pip
    
    pip install oca apache-libcloud
    
    cd /path/to/conpaassql
    python setup.py install
    
    cd /path/to/conpaassql-manager-gui
    python setup.py install
    
    mkdir -p /etc/conpaassql
    
    cat > /etc/conpaassql/manager-gui.conf << EOF
    MANAGER_HOST = '10.1.0.9'
    EOF
    
    screen -S conpaasssql-manager-gui -d -m conpaassql_manager_gui
