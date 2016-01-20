# FROG4 Orchestrator Installation Guide

The installation instructions below have been tested on ubuntu 14.04.1.

#### Required packages
First, you need to install all the required ubuntu packages. For this, please follow the steps below:
    
        sudo apt-get install python3-dev python3-setuptools
		sudo easy_install3 pip
        sudo apt-get install python3-sqlalchemy libmysqlclient-dev
		sudo pip3 install --upgrade falcon requests gunicorn jsonschema pymysql

#### Clone the code
Now you have to clone this repository _and_ all the submodules. Submodules include components that are part of the orchestrator but that are being developed in different repositories. This lead to the necessity to clone them as well in the right folders, under the FROG4 orchestrator root. For this, please follow the steps below:

        git clone https://github.com/netgroup-polito/frog4-orchestrator.git
        cd frog4-orchestrator
        git submodule init && git submodule update


#### Modify the configuration parameters
For this, you need to modify the [configuration/orchestrator.conf](configuration/orchestrator.conf) file according to your preferences.

#### Create database
The FROG4 orchestrator uses a local mySQL database that has to be created and initialized by executing the steps below.

- Create database and user for orchestrator database:
	    
        mysql -u root -p
        mysql> CREATE DATABASE orchestrator;
        mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'localhost' IDENTIFIED BY 'ORCH_DBPASS';
        mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'%' IDENTIFIED BY 'ORCH_DBPASS';	
        mysql> exit;
    
- Create tables in the orchestrator db (all the initialization parameters are stored in the ``db.sql`` file):
    
        mysql -u orchestrator -p orchestrator < db.sql

- Change the the parameters used to connect to the database in [configuration/orchestrator.conf](configuration/orchestrator.conf):

        [db]
        # Mysql DB
        connection = mysql+pymysql://orchestrator:ORCH_DBPASS@127.0.0.1/orchestrator
        
- Change all the templates inside the ``templates`` directory with the correct information.

#### Run the orchestrator
You can launch the orchestrator by executing the following script in the orchestrator root folder:
        
        ./start_orchestrator.sh
