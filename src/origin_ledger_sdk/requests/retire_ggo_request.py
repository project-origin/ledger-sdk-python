
import marshmallow_dataclass

from typing import List
from dataclasses import dataclass, field
from bip32utils import BIP32Key
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from .abstract_request import AbstractRequest
from .helpers import get_signer

from ..ledger_dto import generate_address, AddressPrefix
from ..ledger_dto.requests import RetireGGORequest as LedgerRetireGGORequest
from ..ledger_dto.requests import SettlementRequest as LedgerSettlementRequest

retire_ggo_schema = marshmallow_dataclass.class_schema(LedgerRetireGGORequest)
settlment_schema = marshmallow_dataclass.class_schema(LedgerSettlementRequest)


@dataclass
class RetireGGORequest(AbstractRequest):
    measurement_key: BIP32Key = field()
    ggo_keys: List[BIP32Key] = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        settlement_address = generate_address(AddressPrefix.SETTLEMENT, self.measurement_key.PublicKey())
        measurement_address = generate_address(AddressPrefix.MEASUREMENT, self.measurement_key.PublicKey())

        signed_transaction = []
        addresses = [settlement_address, measurement_address]
        ggo_addresses = []

        for ggo_key in self.ggo_keys:
            
            ggo_address = generate_address(AddressPrefix.GGO, ggo_key.PublicKey())

            retire_request = LedgerRetireGGORequest(
                origin=ggo_address,
                settlement_address=settlement_address
            )

            byte_obj = self._to_bytes(retire_ggo_schema, retire_request)

            transaction = self.sign_transaction(
                batch_signer=batch_signer,
                transaction_signer=get_signer(ggo_key),
                payload_bytes=byte_obj,
                inputs=[ggo_address],
                outputs=[ggo_address],
                family_name=LedgerRetireGGORequest.__name__,
                family_version='0.1')

            addresses.append(ggo_address)
            ggo_addresses.append(ggo_address)
            signed_transaction.append(transaction)



        request = LedgerSettlementRequest(
            settlement_address=settlement_address,
            measurement_address=measurement_address,
            ggo_addresses=ggo_addresses)


        byte_obj = self._to_bytes(settlment_schema, request)

        signed_transaction.append(self.sign_transaction(
            batch_signer=batch_signer,
            transaction_signer=get_signer(self.measurement_key),
            payload_bytes=byte_obj,
            inputs=addresses,
            outputs=[settlement_address],
            family_name=LedgerSettlementRequest.__name__,
            family_version='0.1'))

        return signed_transaction


