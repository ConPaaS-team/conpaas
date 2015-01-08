#!/bin/bash
. log.sh
export DEBIAN_FRONTEND=noninteractive
EMDROS_INSTALL=true
SHEMDROS_INSTALL=true
TOMCAT_INSTALL=true
if $EMDROS_INSTALL
then
if true
then
# 1 Installing Emdros
log -d 0. $0
log -d 1. Installing Emdros 
log -c df -lh
EMDROS_VERSION=3.4.0
EMDROS_DIR=emdros-$EMDROS_VERSION
EMDROS_TARBALL=emdros-$EMDROS_VERSION.tar.gz

log -C apt-get update


log -d "grep 'debian stable main contrib' /etc/apt/sources.list"
grep 'debian stable main contrib' /etc/apt/sources.list >/dev/null || echo "deb http://http.us.debian.org/debian stable main contrib non-free" >>/etc/apt/sources.list 
grep 'debian stable main contrib' /etc/apt/sources.list

log -C apt-get update

#for i in make g++ zlib1g-dev build-essential fakeroot debhelper autotools-dev binutils tcl tcl-dev re2c transfig swig autoconf automake libtool libwxgtk2.8-0 libwxgtk2.8-dev openjdk-7-jdk python-dev mono-devel mono-tools-devel perl libmysqlclient-dev libpq-dev groff imagemagick xdg-utils
log -c apt-get install mysql-server -y
log -c apt-get install g++ -y
for i in binutils swig openjdk-7-jdk libmysqlclient-dev python-dev zip bzip2 maven
do
    if which $i 
    then
        log -s apt-get install $i -y
    else
        case $i in
            xopenjdk-7-jdk)
                OPT=-C
            ;;
            *)
                OPT=-c
            ;;
        esac
        log $OPT apt-get install $i -y
    fi
done

#Not very clearly in INSTALL: mysql libraries:

# done above : apt-get install libmysqlclient-dev -y

log -d Building .debs
log -d 2.  'On Ubuntu Quantal (12.10), the following set of packages -- and their dependencies -- will do:'

log -t apt-get install build-essential fakeroot debhelper -y


log -d 3. Build the .debs.
log -d 3a. 'Place the tarball in a directory, such as $HOME/build.  We will assume you have placed them there for the remainder of this tutorial. '

if [ ! -d ~/build ]
then
    log -c mkdir ~/build
fi

log -d 3b. 

cd ~/build
rm -r *

log -d 3c. 
# download emdros
log -t wget http://sourceforge.net/projects/emdros/files/emdros/$EMDROS_VERSION/$EMDROS_TARBALL/download -O $EMDROS_TARBALL
# tar xfzv emdros-3.4.0.tar.gz
ls -ld emdros-*
log -t tar xfzv $EMDROS_TARBALL
rm $EMDROS_TARBALL

log -d 3d. 

# cd emdros-3.4.0/
log -c cd $EMDROS_DIR/

log -d 3e. 

log -t dpkg-buildpackage -rfakeroot

# This should build the .debs in $HOME/build/.  If this fails with an error, or it builds a .deb with a wrong version, _please_ get in touch with the Emdros author, Ulrik Sandborg-Petersen, by email:
# ulrikp<at>emdros|dot|org.  Thanks in advance for your help!


log -d 4. Install the .debs

log -c cd ~/build
log -t dpkg -i emdros_3.4.0-1_amd64.deb



log -d Check:
log -s man mql
log -c mql --help

log -t apt-get install bzip2
fi

if true
then
log -d EMDROS DATA
log -c df -lh
# The etcbc4 mql database can be loaded as follows.
# Here is a link to the bzipped source: https://www.dropbox.com/s/tqg5vvz8qypqmvl/etcbc4.mql.bz2?dl=0 (23 MB, unzipped ~ 400 MB).
log -t wget 'https://www.dropbox.com/s/tqg5vvz8qypqmvl/etcbc4.mql.bz2?dl=0' -O etcbc4.mql.bz2
log -c df -lh
log -T bunzip2 etcbc4.mql.bz2
log -c df -lh

log -C service mysql status
log -C service mysql restart
log -d "Set up Grants for MySql"

# as we are root during this installation, we don't have to supply username/password
mysql << EOF
GRANT ALL PRIVILEGES ON etcbc4.* TO etcbc@localhost IDENTIFIED BY 'some_password' WITH GRANT OPTION;
GRANT SELECT ON etcbc4.* TO shemdros@localhost IDENTIFIED BY 'some_password' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# Checking:
SELECT User, Host, Password FROM mysql.user;
SHOW GRANTS FOR 'etcbc'@'localhost';
EOF

fi
log -C service mysql status
log -C service mysql restart

log -c cd ~/build
log -d Drop database
# again, we don't have to supply username/password
mysql << EOF
drop database etcbc4;
EOF

log -d Load database
cat etcbc4.mql | log -c mql -b m -u etcbc -p some_password # < etcbc4.mql
#mql -b m -u etcbc -p 'some_password' < etcbc4.mql 2>/dev/shm/etcbc4.err

log -d Emdros installation finished
log -c df -lh
fi # EMDROS_INSTALL

if $SHEMDROS_INSTALL
then
log -d 4. Installing Shemdros 
log -c df -lh
log -d echo =================================
if true
then
git clone https://github.com/Dans-labs/shemdros.git
# https://github.com/Dans-labs/shemdros/archive/master.zip
fi
log -c df -lh
log -d Shemdros installation finished
fi


if $TOMCAT_INSTALL
then
log -d 5. Installing Tomcat6
log -c apt-get install tomcat6 -y

#       echo >mql-test.txt "select all objects where [verse [word focus lex='CBLT/'] .. [word focus lex='SBLT/'] ]"
#       cp /root/build/shemdros/pom.xml /etc/tomcat6/Catalina/localhost
fi

#root@conpaas:~# mkdir -p /var/lib/tomcat6/webapps/shemdros/WEB-INF/classes
#root@conpaas:~# cp build/shemdros/src/main/resources/applicationContext.xml /var/lib/tomcat6/webapps/shemdros/WEB-INF/classes
#root@conpaas:~# cp build/shemdros/src/main/webapp/WEB-INF/web.xml /var/lib/tomcat6/webapps/shemdros/WEB-INF/classes
#root@conpaas:~# cp build/shemdros/src/main/webapp/WEB-INF/logback.xml /var/lib/tomcat6/webapps/shemdros/WEB-INF/classes
#root@conpaas:~# cp build/shemdros/src/main/webapp/WEB-INF/*.xml /var/lib/tomcat6/webapps/shemdros/WEB-INF/classes
#root@conpaas:~# cp build/shemdros/src/main/resources/logback.xml /var/lib/tomcat6/webapps/shemdros/WEB-INF/classes


# =============================================
#       exit
#       ==> mql-test.sh <==
#       mql mql-test.txt

#       ==> mql-test.txt <==
#       select all objects where [verse [word focus lex='CBLT/'] .. [word focus lex='SBLT/'] ]


#	 
#	looks like I need to install web2py, see
#	https://www.digitalocean.com/community/tutorials/how-to-use-the-web2py-framework-to-quickly-build-your-python-app
#	
#	
#	
#	Install the Web2py Software
#	
#	Your Ubuntu server instance should already come with Python installed by default. This takes care of one of the only things that web2py needs to run successfully.
#	
#	The only other software that we need to install is the unzip package, so that we can extract the web2py files from the zip file we will be downloading:
#	
#	sudo apt-get update
#	sudo apt-get install unzip
#	
#	Now, we can get the framework from the project''s website. We will download this to our home folder:
#	
#	cd ~
#	wget http://www.web2py.com/examples/static/web2py_src.zip
#	
#	Now, we can unzip the file we just downloaded and move inside:
#	
#	unzip web2py_src.zip
#	cd web2py
#	
#	Now that we are inside the web2py directory, how do we install it? Well, one of the great things about web2py is that you do not install it. You can run it right from this folder by typing:
#	
#	python web2py.py
#	
#	However, this will only launch the web interface that is accessible on the local machine. This is a security feature, but it doesn''t help us since our framework is being hosted on a remote droplet.
#	
#	To stop the server, typing "CTRL-C" in the terminal. We will sort out the web access issue momentarily.
#	Create SSL Certificates to Allow Remote Access
#	
#	To allow remote access, we must start the web framework with SSL. We need to create our certificates before we can do that. Luckily, the openssl package is already installed.
#	
#	We can create an RSA key to use for certificate generation with the following command:
#	
#	openssl genrsa -out server.key 2048
#	
#	Using this key, we can then generate the .csr file:
#	
#	openssl req -new -key server.key -out server.csr
#	
#	Finally, we can use these two pieces to create an SSL certificate:
#	
#	openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
#	
#	You should now have a server.key, server.csr, and server.crt file in your web2py directory. We can use these to start up the interface in a secure manner by passing some parameters to web2py when we call it:
#	
#	python web2py.py -a 'admin_password' -c server.crt -k server.key -i 0.0.0.0 -p 8000
#	
#	You can select whichever password you would like to use to log into your framework web interface. The "0.0.0.0" allows this to be accessible to remote systems.
#	
#	You can access the interface by visiting:
#	
#	https://your_ip:8000
#	
#	
