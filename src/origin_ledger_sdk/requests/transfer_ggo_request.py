

from .abstract_request import AbstractRequest
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from bip32utils import BIP32Key
from typing import List

from dataclasses import dataclass, field
import marshmallow_dataclass
from .helpers import get_signer

from ..ledger_dto import generate_address, AddressPrefix
from ..ledger_dto.requests import TransferGGORequest as LedgerTransferGGORequest

transfer_ggo_schema = marshmallow_dataclass.class_schema(LedgerTransferGGORequest)


@dataclass
class TransferGGORequest(AbstractRequest):
    current_key: BIP32Key = field()
    new_address: str = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        ggo_address = generate_address(AddressPrefix.GGO, self.current_key.PublicKey())

        request = LedgerTransferGGORequest(
            origin=ggo_address,
            destination=self.new_address
        )

        byte_obj = self._to_bytes(transfer_ggo_schema, request)

        return [self.sign_transaction(
            batch_signer,
            get_signer(self.current_key),
            byte_obj,
            inputs=[ggo_address, self.new_address],
            outputs=[ggo_address, self.new_address],
            family_name=LedgerTransferGGORequest.__name__,
            family_version='0.1')]  
