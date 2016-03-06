Use this guide to get a working copy of the statistics system on your system.

## Install needed packages

List of software you must install using your package manager (package names are for Fedora (dnf)):

* `python2` - language used
* `libxml2` and `libxml2-devel` - used for installing another dependency
* `PyQt4` and `PyQt4-devel` - dependency for another dependency
* `numpy` - making calculations
* `python2-matplotlib` - creating graphs over listeners the past day
* `rabbitmq-server` - running reoccuring tasks
* `gcc` - dependency for another dependency
* `libXtst` and `libXtst-devel` - dependency for another dependency

## Download the project and create virtual environment

Clone this repository, move inside the repository and run

```sh
virtualenv -p python2.7 venv
```

Whenever you want to do anything with this project, you must first activate the virtual environment by running:

```sh
source venv/bin/activate
```

When you want to use the terminal for something else:

```sh
deactivate
```

## Install required python packages

Make sure you've activated the virtual environment, then run

```sh
pip install -r requirements.txt
```

## Initialize Django-installation

Google "how to set up django project in production"