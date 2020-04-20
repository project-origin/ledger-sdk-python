
# Ledger-SDK

The goal of this repository is to create a simple and common way to interact with the Ledger of Origins that is a part of Project Origin.

This is work in progress, more documentation will be written as the project progresses.


# Keys

TODO: A whole section where there will be info on key management.

# Using the SDK

There are a number of request that can be executed to the ledger, these are:

* PublishMeasurementRequest
* IssueGGORequest
* TransferGGORequest
* SplitGGORequest
* RetireGGORequest

The first two are only for issuing bodies, and will be denied if tried.

To execute a request one must first import the ledger, batch and a request type

    from origin_ledger_sdk import Ledger, Batch, TransferGGORequest



## Transfer request

Next one can create a new TransferGGORequest, This request requires two keys as input.
First key should be the private extended key that contains a GGO.
Second should be the address where the GGO must be transferred to.
    
    request = TransferGGORequest(
        current_key=owner_key,
        new_address=reciepient_address,
    )

## Batch

After the request has been created, we must create a batch using a another key.
And then the request is added to the batch.
Multiple request can be added to the same batch. Which insures all or none of the transactions are executed.

        batch = Batch(signer_key=key)
        batch.add_request(request)

BEWARE - everything done in one batch can be seen by anyone as a single batch and therefore know they have been performed by the same entity. So one should be careful about what one bundles in a single batch.

## Executing a batch

Last thing to do is to send the batch to the ledger.
Create an instance of the Ledger with the url to the public endpoint
Everything on the ledger is asynchronous, so a handle is returned, on which a user can request the status of the batch.

    ledger = Ledger('https://url-to-ledger')

    # Send the batch to the ledger to execute.
    handle = ledger.execute_batch(batch) 

    # Request status of the batch.
    status = ledger.get_batch_status(handle)


# Source code

Make sure to upgrade your system packages for good measure:
   
    pip install --upgrade --user setuptools pip pipenv

Then install project dependencies:

    pipenv install

To run the tests:
    
    pipenv run pytest


# Push to pypi

    python3 setup.py bdist_wheel
    python3 -m twine upload dist/*