# OCT-TURRETS-PY

# What is oct-turrets ?

This repository contain the default "turret" (the client) for the OCT testing library.
This package is a dependecy of OCT but is more a "cookbook" for how to build your own turret.

As you can see the turret has only three requirements : argparse for the command line tools, six for the py2/py3
compatibilty and pyzmq for the communication with the HQ (oct-core)

The turret will be in charge of running the tests an simulate multiples users, but it only need a configuration and a
test file to run.

Python Version | Tested |
-------------- | -------|
Python >= 2.7.x|OK|
Python >= 3.4|OK|

## Installation

Simply run :

```
pip install oct-turrets
```

Or from the source :

```
python setup.py install
```

## Usage

For starting the turret you have two option :

* call it with a json valid configuration file. **Warning** the script file to run for the tests will be load based on
the configuration key `script`, but for loading it the turret will use the path of the configuration file as base directory

```
oct-turret-start --config-file config.json
```

* call it with a tar archive containing a valid configuration file and the associated test script

```
oct-turret-start --tar my_turret.tar
```
