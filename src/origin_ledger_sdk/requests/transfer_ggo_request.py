
import marshmallow_dataclass

from typing import List
from dataclasses import dataclass, field
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from .abstract_request import AbstractRequest
from .helpers import get_signer
from ..ledger_dto.requests import TransferGGORequest as LedgerTransferGGORequest

transfer_ggo_schema = marshmallow_dataclass.class_schema(LedgerTransferGGORequest)


@dataclass
class TransferGGORequest(AbstractRequest):
    """
    :param bytes source_private_key The source private key as a byte-string of the GGO to transfer
    :param str source_address The source address of the GGO to transfer
    :param str destination_address The destination address of where to move the GGO
    """

    source_private_key: bytes = field()
    source_address: str = field()
    destination_address: str = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        request = LedgerTransferGGORequest(
            origin=self.source_address,
            destination=self.destination_address
        )

        byte_obj = self._to_bytes(transfer_ggo_schema, request)

        return [self.sign_transaction(
            batch_signer,
            get_signer(self.source_private_key),
            byte_obj,
            inputs=[self.source_address, self.destination_address],
            outputs=[self.source_address, self.destination_address],
            family_name=LedgerTransferGGORequest.__name__,
            family_version='0.1')]  