
import marshmallow_dataclass

from typing import List
from dataclasses import dataclass, field
from bip32utils import BIP32Key
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from .abstract_request import AbstractRequest
from .helpers import get_signer, generate_address, AddressPrefix

from ..ledger_dto.requests import LedgerRetireGGORequest, LedgerSettlementRequest

retire_ggo_schema = marshmallow_dataclass.class_schema(LedgerRetireGGORequest)
settlement_schema = marshmallow_dataclass.class_schema(LedgerSettlementRequest)

@dataclass
class RetireGGORequest(AbstractRequest):
    measurement_key: BIP32Key = field()
    ggo_keys: List[BIP32Key] = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        settlement_address = generate_address(AddressPrefix.GGO, self.measurement_key)
        measurement_address = generate_address(AddressPrefix.MEASUREMENT, self.measurement_key)
        
        addresses = [settlement_address, measurement_address]
        signed_transactions = []

        for ggo_key in self.ggo_keys:
            ggo_address = generate_address(AddressPrefix.GGO, ggo_key)
            addresses.append(ggo_address)

            ggo_signer = get_signer(self.ggo_key)

            request = LedgerRetireGGORequest(settlement_address)
            byte_obj = self._to_bytes(retire_ggo_schema, request)

            signed_transaction = self.sign_transaction(
                batch_signer=batch_signer,
                transaction_signer=ggo_signer,
                payload_bytes=byte_obj,
                inputs=[ggo_address],
                outputs=[ggo_address],
                family_name='datahub',
                family_version='0.1')

            signed_transactions.append(signed_transaction)

        request = LedgerSettlementRequest(
            measurement_address=measurement_address,
            settlement_address=settlement_address,
            ggo_addresses=addresses
        )

        transaction_signer = get_signer(self.measurement_key)
        byte_obj = self._to_bytes(settlement_schema, request)

        signed_transaction = self.sign_transaction(
            batch_signer=batch_signer,
            transaction_signer=transaction_signer,
            payload_bytes=byte_obj,
            inputs=addresses,
            outputs=[settlement_address],
            family_name='datahub',
            family_version='0.1')

        signed_transactions.append(signed_transaction)
        
        return signed_transactions


