__author__ = 'dcortes'

from schematics.types import StringType, FloatType
from schematics.types.compound import ListType, ModelType

from dexma_api_v3.factory.reference_device import ReferenceDevice
from dexma_api_v3.factory.location_factory.location_info_factory.address import Address
from dexma_api_v3.factory.base_entity import BaseEntity
from dexma_api_v3.factory.custom_types.unsigned_long import UnsignedLong
from dexma_api_v3.factory.custom_types.nullable_float_type import NullableFloatType


class Leaf(BaseEntity):

    name = StringType(required=True)
    type = StringType(required=True)
    parent =  ModelType(BaseEntity, required=True)
    area = NullableFloatType(required=True)
    summer_temp = NullableFloatType(required=True)
    winter_temp = NullableFloatType(required=True)
    activity = StringType(required=True)
    reference_devices = ListType(ModelType(ReferenceDevice, required=True))
    address = ModelType(Address, required=True)


