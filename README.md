### SETUP

## Get your Youtube API key
You will need to acquire a YouTube v3 API key, which you can do so easily [here](https://console.developers.google.com/cloud-resource-manager). After obtaining the API key, enter it as a string into the config.yaml file

## Environment Setup
Create a virtual environment (built-in venv module) using the below command on your project folder so it should look like below;
```
python -m venv your_env_name
```

Activate your environment;
```
source your_env_name/bin/activate
```

If you need to deactivate your environment you can use the command below but this is not the case for this project;
```
deactivate
```

You can display your installed packages;
```
pip list
```

You should be able to see something like this on the console so as we can see, we only have the pip and setuptools packages.
```
Package    Version
---------- -------
pip        20.2.4
setuptools 49.2.1
```

## Complete setup
You can easily setup the environment and required packages using the command below, but if you want, you can follow the manual setup steps as well for better understanding
Install the packages using requirements.txt file on the virtual environment.
```
pip install -r requirements.txt
```

## Execution

Initialize the database with below commands
```
airflow db init
```
```
airflow users create \
    --username admin \
    --firstname your_name \
    --lastname your_surname \
    --role Admin \
    --email your_email@something.com
```

Start the web server, default port is 8080
```
airflow webserver --port 8080
```

If you get an Error like below;
```
Error: No module named 'airflow.www'; 'airflow' is not a package
```

Start the scheduler
```
airflow scheduler
```

Now you can enter your airflow interface by typing your username as admin and password. Trigger your DAG and see the results On the interface.

## Airflow Setup
You don't need to follow this part if you already installed he requirements. I shared it for the ones who want to setup Apache Airflow Manually.
Following along the official Apache Airflow documentation definitely helps a lot, please do follow that the below steps are taken from there already.

Upgrade or downgrade your pip version to the version below; This version is suggested by airflow official document
```
pip install --upgrade pip==20.2.4
```

Airflow needs a home, ~/airflow is the default, Set the AIRFLOW_HOME variable. This folder contains the airflow and the related data
```
export AIRFLOW_HOME=~/airflow
```

Set the AIRFLOW_VERSION variable
```
export AIRFLOW_VERSION=2.0.1
```

Set the PYTHON_VERSION variable
```
export PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
```

Set the CONSTRAINT_URL variable
```
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
```

Now you are ready for a painless Airflow installation using pip
```
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

You can run the below command which downloads gunicorn which is a Python WSGI HTTP Server for UNIX
```
pip install gunicorn==19.5.0
```
