import requests
import base64
import json
import marshmallow_dataclass

from typing import List #, Optional
from dataclasses import dataclass, field
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from marshmallow_dataclass import class_schema

from .batch import Batch, BatchStatus
from .ledger_dto import Measurement, GGO


class LedgerException(Exception):
    def __init__(self, message, code=None):
        super(LedgerException, self).__init__(message)
        self.code = code


@dataclass
class Error:
    code: int = field()
    message: str = field()
    title: str = field()


@dataclass
class Handle:
    link: str = field(default=None)
    error: Error = field(default=None)


@dataclass
class Paging:
    limit: int = field()
    start: int = field()


@dataclass
class InvalidTransaction:
    id: str = field()
    message: str = field()


@dataclass
class BatchStatusResponse:
    id: str = field()
    status: BatchStatus = field()
    invalid_transactions: List[InvalidTransaction] = field(default=None)


@dataclass
class BatchStatusResponseHeader:
    data: List[BatchStatusResponse] = field()
    link: str = field()


@dataclass
class StateResponse:
    data: str = field()
    head: str = field()
    link: str = field()


handle_schema = marshmallow_dataclass.class_schema(Handle)()
batch_status_schema = marshmallow_dataclass.class_schema(BatchStatusResponseHeader)()
state_response_schema = marshmallow_dataclass.class_schema(StateResponse)()
measurement_schema = class_schema(Measurement)()
ggo_schema = class_schema(GGO)()


class Ledger(object):

    def __init__(self, url):
        self.url = url

    def execute_batch(self, batch: Batch) -> str:
        signed_batch = batch.get_signed_batch()
        return self._send_batches([signed_batch])

    def get_batch_status(self, link: str) -> BatchStatusResponse:
        response = requests.get(link)

        print("\nRESPONSE:", response.content, "\n\n")

        batch_status = batch_status_schema.loads(response.content)

        return batch_status.data[0]

    def _send_batches(self, signed_batches) -> str:
        batch_list_bytes = BatchList(batches=signed_batches).SerializeToString()

        try:
            response = requests.post(
                f'{self.url}/batches',
                batch_list_bytes,
                headers={'Content-Type': 'application/octet-stream'})

            handle: Handle = handle_schema.loads(response.content)

            if handle.error is not None:
                raise LedgerException(handle.error.message, handle.error.code)

            return handle.link

        except json.decoder.JSONDecodeError:
            raise LedgerException(f'Invalid response from Ledger "{response.content.decode()}"')

    def _get_state(self, address) -> StateResponse:
        response = requests.get(
            f'{self.url}/state/{address}'
        )

        return state_response_schema.loads(response.content)

    def get_measurement(self, address: str) -> Measurement:
        response = self._get_state(address)
        
        body = base64.b64decode(response.data)

        measurement = measurement_schema.loads(body)
        measurement.address = address

        return measurement

    def get_ggo(self, address: str) -> GGO:
        response = self._get_state(address)
        
        body = base64.b64decode(response.data)

        ggo = ggo_schema.loads(body)
        ggo.address = address

        return ggo
