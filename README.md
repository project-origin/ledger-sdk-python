
# Ledger-SDK

The goal of this repository is to create a simple and common way to interact with the Ledger of Origins that is a part of Project Origin.

This is work in progress, more documentataion will be written as the project progresses.

# Test

Make sure to upgrade your system packages for good measure:
   
    pip install --upgrade --user setuptools pip pipenv

Then install project dependencies:

    pipenv install

Requirements,
Currently the tests are written as integrations tests.
Requiring the ledger to be running locally.

To run the tests:
    
    pipenv run pytest


