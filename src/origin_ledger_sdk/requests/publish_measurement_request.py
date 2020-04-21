

import marshmallow_dataclass

from datetime import datetime
from typing import List
from dataclasses import dataclass, field
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from .abstract_request import AbstractRequest

from ..ledger_dto.requests import PublishMeasurementRequest as LedgerPublishMeasurementRequest
from ..ledger_dto import MeasurementType

measurement_schema = marshmallow_dataclass.class_schema(LedgerPublishMeasurementRequest)


@dataclass
class PublishMeasurementRequest(AbstractRequest):
    """
    :param str address: The address where to publish the measurement.
    :param datetime begin: The datetime where the measurement begins.
    :param datetime end: The datetime where the measurement ends.
    :param str sector: The sector (price-zone) where the measurement occurred.
    :param MeasurementType type: The type of measurement (Production | Consumption)
    :param int amount: The amount of power in Wh.
    """

    address: str = field()
    begin: datetime = field()
    end: datetime = field()
    sector: str = field()
    type: MeasurementType = field()
    amount: int = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

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
            inputs=[self.address],
            outputs=[self.address], 
            family_name=LedgerPublishMeasurementRequest.__name__,
            family_version='0.1')] 

