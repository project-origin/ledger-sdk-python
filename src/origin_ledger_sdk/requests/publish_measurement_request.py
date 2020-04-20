

from datetime import datetime
from .abstract_request import AbstractRequest
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from bip32utils import BIP32Key
from typing import List

from dataclasses import dataclass, field
import marshmallow_dataclass

from ..ledger_dto.requests import PublishMeasurementRequest as LedgerPublishMeasurementRequest
from ..ledger_dto import MeasurementType, generate_address, AddressPrefix

measurement_schema = marshmallow_dataclass.class_schema(LedgerPublishMeasurementRequest)


@dataclass
class PublishMeasurementRequest(AbstractRequest):
    owner_key: BIP32Key = field()
    begin: datetime = field()
    end: datetime = field()
    sector: str = field()
    type: MeasurementType = field()
    amount: int = field()
    

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        address = generate_address(AddressPrefix.MEASUREMENT, self.owner_key.PublicKey())

        measurement = LedgerPublishMeasurementRequest(
            begin=self.begin,
            end=self.end,
            sector=self.sector,
            amount=self.amount,
            type=self.type
            )    

        bytez = self._to_bytes(measurement_schema, measurement)
 
        return [self.sign_transaction(
            batch_signer,
            batch_signer,
            bytez,
            inputs=[address],
            outputs=[address], 
            family_name=LedgerPublishMeasurementRequest.__name__,
            family_version='0.1')] 

