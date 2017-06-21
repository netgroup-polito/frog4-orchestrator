# FROG4 Orchestrator Installation Guide

The installation instructions below have been tested on ubuntu 14.04.3.

## Required packages
First, you need to install all the required ubuntu packages. For this, please follow the steps below:

	sudo apt-get install python3-dev python3-setuptools python3-pip python3-sqlalchemy libmysqlclient-dev mysql-server
	sudo pip3 install --upgrade requests gunicorn jsonschema pymysql flask flask-restplus Flask-SQLAlchemy

## Clone the code
Now you have to clone this repository _and_ all the submodules. Submodules include components that are part of the orchestrator but that are being developed in different repositories. This lead to the necessity to clone them as well in the right folders, under the FROG4 orchestrator root. For this, please follow the steps below:

        git clone https://github.com/netgroup-polito/frog4-orchestrator.git
        cd frog4-orchestrator
        git submodule init && git submodule update

## DoubleDecker client
The frog4-orchestrator uses the [DoubleDecker](https://github.com/Acreo/DoubleDecker-py) messaging system to communicate with the domain orchestrators. In order to launch the frog4-orchestrator you need to install DoubleDecker, if it is not already installed.

		$ git clone https://github.com/Acreo/DoubleDecker-py.git
		$ cd DoubleDecker-py
Now you can follow the instruction provided in that folder. You can choose to install it in your system (recommended if you are installing also other frog4 components) or simply copy the doubledecker folder in the [orchestrator_core](orchestrator_core) folder with the following command:

		cp -R DoubleDecker-py/ {orchestrator_root}/orchestrator_core/
In this way the frog4-orchestrator will use the DoubleDecker sources in his folder, otherwise it will use the installed version, if present.

## FROG-orchestrator Configuration file
For this, you need to modify the [config/default-config.ini](config/default-config.ini) file according to your preferences.
Important parameters to be properly set are the following:
* (broker)[https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L26]: this line must point to the broker previously installed
* (templates repository)[https://github.com/netgroup-polito/frog4-orchestrator/blob/master/config/default-config.ini#L53]: this line typically points to the [frog4-datastore](https://github.com/netgroup-polito/frog4-datastore) containing the NF templates. 

#### Create database
The FROG4 orchestrator uses a local mySQL database that has to be created and initialized by executing the steps below.

- Create database and user for orchestrator database:
	    
       	mysql -u root -p
       	mysql> CREATE DATABASE orchestrator;
       	mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'localhost' IDENTIFIED BY 'ORCH_DBPASS';
       	mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'%' IDENTIFIED BY 'ORCH_DBPASS';
       	mysql> exit;
    
- Create tables in the orchestrator db (all the initialization parameters are stored in the ``db.sql`` file):
    
        mysql -u orchestrator -p -Dorchestrator < db.sql

- Change the the parameters used to connect to the database in the configuration file:

        [db]
        # Mysql DB
        connection = mysql+pymysql://orchestrator:ORCH_DBPASS@127.0.0.1/orchestrator
        
#### Run the orchestrator
You can launch the orchestrator by executing the following script in the orchestrator root folder, optionally specifying the configuration file (example: conf/config.ini):
        
        ./start_orchestrator.sh [--d conf-file]

#### Useful scripts
You can find some helpful scripts inside the [scripts](scripts) folder. For example, if you need to clean all sessions and graphs currently stored in the database, you can launch the following script in the orchestrator root folder:
        
        python3 -m scripts.clean_db_sessions

The same applies for other similar scripts like [clean_domains_and_info](scripts/clean_domains_and_info.py) that will remove data related to the domains connected to the orchestrator from the database. You just need to replace "clean_db_sessions" with "clean_domains_and_info" in the previous command.
