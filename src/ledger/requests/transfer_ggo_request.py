

from .abstract_request import AbstractRequest
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from bip32utils import BIP32Key
from typing import List

from dataclasses import dataclass, field
import marshmallow_dataclass
from .helpers import get_signer, generate_address, AddressPrefix

@dataclass
class LedgerTransferGGORequest:
    key: str = field()

transfer_ggo_schema = marshmallow_dataclass.class_schema(LedgerTransferGGORequest)


@dataclass
class TransferGGORequest(AbstractRequest):
    current_key: BIP32Key = field()
    new_key: BIP32Key = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        ggo_address = generate_address(AddressPrefix.GGO, self.current_key)
        new_address = generate_address(AddressPrefix.MEASUREMENT, self.new_key)

        request = LedgerTransferGGORequest(
            key=self.new_key.PublicKey().hex()
        )

        byte_obj = self._to_bytes(transfer_ggo_schema, request)

        return [self.sign_transaction(
            batch_signer,
            get_signer(self.current_key),
            byte_obj,
            inputs=[ggo_address, new_address],
            outputs=[ggo_address, new_address],
            family_name='datahub',
            family_version='0.1')]  
