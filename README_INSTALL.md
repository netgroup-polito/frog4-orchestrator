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
		$ sudo python3 setup.py install
## Create the SQL database
The FROG4 orchestrator uses a local mySQL database that has to be created and initialized by executing the steps below.

- Create database and user for orchestrator database:
	    
       	mysql -u root -p
       	mysql> CREATE DATABASE orchestrator;
       	mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orch-user'@'localhost' IDENTIFIED BY 'orch-pwd';
       	mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orch-user'@'%' IDENTIFIED BY 'orch-pwd';
       	mysql> exit;

where `orch-user` and `orch-pwd` can be replaced respectively by the username and the password that the FROG4-orchestator will use to access to the SQL database.
    
- Create tables in the orchestrator db (all the initialization parameters are stored in the ``db.sql`` file):

        $ cd [frog4-orchestrator]
        $ mysql -u orch-user -p -Dorchestrator < db.sql

  When it asks the password, enter that used above (i.e., `orch-pwd`). The process may take some seconds.
  
  The script above also adds in the database the `admin` user (`username:admin`, `password:admin`).

### Create a new user
To create a new user, runs:

        $ cd [frog4-orchestrator]
        $ python3 -m scripts.create_user

To add a new user on the database

## FROG-orchestrator configuration file
For this, you need to modify the [config/default-config.ini](config/default-config.ini) file according to your preferences.
Important parameters to be properly set are the following:
* [broker address](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L26): this line must point to the broker previously installed;
* [dd_keyfile](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L28): this line must point to a local file containing the key to be used on the message bus;
* [templates repository_url](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L53): this line typically points to the [frog4-datastore](https://github.com/netgroup-polito/frog4-datastore) containing the NF templates. 
* [db connection](https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L40): this line must be changed so that `orch-user` and `orch-pwd` are set to the value chose above when creating the SQL database.

Moreover, in this file you can set the TCP port to be used to interact with the FROG4-orchestrator through its REST API.

# Run the orchestrator
You can launch the FROG4-orchestrator by executing the following script in the orchestrator root folder, optionally specifying the configuration file (example: conf/config.ini):
        
        $ cd [frog4-orchestrator]
        $ ./start_orchestrator.sh [--d conf-file]
	
# How to interact with the FROG4-orchestrator

A description of the API exposed by the FROG4-orchestrator is available at the URL: `ip_address:port/api_docs` (e.g., `127.0.0.1:9000/api_docs`).

## Adding the WEB GUI on top of the SDN domain orchestrator

It is possible to configure the [FROG4 GUI](https://github.com/netgroup-polito/fg-gui), so that it can be used to interact with the FROG4-orchestrator (e.g., to deploye new service graphs, or to read the service graphs currently deployed).
To install the GUI, follows the [instructions](https://github.com/netgroup-polito/fg-gui/blob/master/README_INSTALL.md) provided with the repository.

# Useful scripts
You can find some helpful scripts inside the [scripts](scripts) folder. For example, if you need to clean all sessions and graphs currently stored in the database, you can launch the following script in the orchestrator root folder:
        
        python3 -m scripts.clean_db_sessions

The same applies for other similar scripts like [clean_domains_and_info](scripts/clean_domains_and_info.py) that will remove data related to the domains connected to the orchestrator from the database. You just need to replace "clean_db_sessions" with "clean_domains_and_info" in the previous command.
