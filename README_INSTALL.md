# FROG4 Orchestrator Installation Guide

The following instructions have been tested on Ubuntu 15.10 and 16.04.

## Required packages
First, you need to install all the required ubuntu packages. For this, please follow the steps below:

	sudo apt-get install python3-dev python3-setuptools python3-pip python3-sqlalchemy libmysqlclient-dev mysql-server
	sudo pip3 install --upgrade requests gunicorn jsonschema pymysql flask flask-restplus Flask-SQLAlchemy

## Clone the code
Now you have to clone this repository _and_ all the submodules. Submodules include components that are part of the orchestrator but that are being developed in different repositories. This lead to the necessity to clone them as well in the right folders, under the FROG4 orchestrator root. For this, please follow the steps below:

        git clone https://github.com/netgroup-polito/frog4-orchestrator.git
        cd frog4-orchestrator
        git submodule init && git submodule update

## Install the DoubleDecker client
The frog4-orchestrator uses the [DoubleDecker](https://github.com/Acreo/DoubleDecker-py) messaging system to communicate with the domain orchestrators. Then, you need to install the DoubleDecker client.

		$ git clone https://github.com/Acreo/DoubleDecker-py.git		
		$ cd DoubleDecker-py
		$ git reset --hard dc556c7eb30e4c90a66e2e00a70dfb8833b2a652
		$ cp -r [frog4-orchestrator]/patches .
		$ git am patches/doubledecker_client_python/0001-version-protocol-rollbacked-to-v3.patch
		
Now you can install the DubleDeker as follows:

		#install dependencies 
		$ sudo apt-get update
		$ sudo apt-get install python3-setuptools python3-nacl python3-zmq python3-urwid python3-tornado
		# install the doubledecker module and scripts
		$ cd DoubleDecker-py
		$ sudo python3 setup.py install
## Create the SQL database
The FROG4 orchestrator uses a local mySQL database that has to be created and initialized by executing the steps below.

- Create database and user for orchestrator database:
	    
       	mysql -u root -p
       	mysql> CREATE DATABASE orchestrator;
       	mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'localhost' IDENTIFIED BY 'ORCH_DBPASS';
       	mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'%' IDENTIFIED BY 'ORCH_DBPASS';
       	mysql> exit;
    
- Create tables in the orchestrator db (all the initialization parameters are stored in the ``db.sql`` file):

        $ cd [frog4-orchestrator]
        mysql -u orchestrator -p -Dorchestrator < db.sql

- Change the the parameters used to connect to the database in the configuration file:

        [db]
        # Mysql DB
        connection = mysql+pymysql://orchestrator:ORCH_DBPASS@127.0.0.1/orchestrator

## FROG-orchestrator Configuration file
For this, you need to modify the [config/default-config.ini](config/default-config.ini) file according to your preferences.
Important parameters to be properly set are the following:
* [broker address](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L26): this line must point to the broker previously installed;
* [dd_keyfile](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L28): this line must point to a local file containing the key to be used on the message bus;
* [templates repository_url](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L53): this line typically points to the [frog4-datastore](https://github.com/netgroup-polito/frog4-datastore) containing the NF templates. 

        
#### Run the orchestrator
You can launch the orchestrator by executing the following script in the orchestrator root folder, optionally specifying the configuration file (example: conf/config.ini):
        
        ./start_orchestrator.sh [--d conf-file]

#### Useful scripts
You can find some helpful scripts inside the [scripts](scripts) folder. For example, if you need to clean all sessions and graphs currently stored in the database, you can launch the following script in the orchestrator root folder:
        
        python3 -m scripts.clean_db_sessions

The same applies for other similar scripts like [clean_domains_and_info](scripts/clean_domains_and_info.py) that will remove data related to the domains connected to the orchestrator from the database. You just need to replace "clean_db_sessions" with "clean_domains_and_info" in the previous command.
