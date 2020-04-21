
import marshmallow_dataclass

from typing import List
from dataclasses import dataclass, field
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from .abstract_request import AbstractRequest
from .helpers import get_signer

from ..ledger_dto.requests import RetireGGORequest as LedgerRetireGGORequest
from ..ledger_dto.requests import SettlementRequest as LedgerSettlementRequest

retire_ggo_schema = marshmallow_dataclass.class_schema(LedgerRetireGGORequest)
settlment_schema = marshmallow_dataclass.class_schema(LedgerSettlementRequest)


@dataclass
class RetireGGOPart():
    """
    :param str address: The address of the GGO to retire.
    :param bytes private_key: The private key of the GGO
    """
    address: str = field()
    private_key: bytes = field()


@dataclass
class RetireGGORequest(AbstractRequest):
    """
    :param str settlement_address: The address of where to create the settlement for a measurement.
    :param str measurement_address: The address of the measurement to retire GGOs to.
    :param bytes measurement_private_key: The owners private key of the measurement.
    :param List[RetireGGOPart] parts: The GGOs to retire to the settlement.
    """

    settlement_address: str = field()
    measurement_address: str = field()
    measurement_private_key: bytes = field()
    parts: List[RetireGGOPart] = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        signed_transaction = []
        addresses = [self.settlement_address, self.measurement_address]
        ggo_addresses = []

        for part in self.parts:
            
            retire_request = LedgerRetireGGORequest(
                origin=part.address,
                settlement_address=self.settlement_address
            )

            byte_obj = self._to_bytes(retire_ggo_schema, retire_request)

            transaction = self.sign_transaction(
                batch_signer=batch_signer,
                transaction_signer=get_signer(part.private_key),
                payload_bytes=byte_obj,
                inputs=[part.address],
                outputs=[part.address],
                family_name=LedgerRetireGGORequest.__name__,
                family_version='0.1')

            addresses.append(part.address)
            ggo_addresses.append(part.address)
            signed_transaction.append(transaction)


        request = LedgerSettlementRequest(
            settlement_address=self.settlement_address,
            measurement_address=self.measurement_address,
            ggo_addresses=ggo_addresses)


        byte_obj = self._to_bytes(settlment_schema, request)

        signed_transaction.append(self.sign_transaction(
            batch_signer=batch_signer,
            transaction_signer=get_signer(self.measurement_private_key),
            payload_bytes=byte_obj,
            inputs=addresses,
            outputs=[self.settlement_address],
            family_name=LedgerSettlementRequest.__name__,
            family_version='0.1'))

        return signed_transaction


