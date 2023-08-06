__author__ = 'dcortes'

from schematics.types import StringType, FloatType
from schematics.types.compound import ListType, ModelType

from dexma_api_v3.factory.reference_device import ReferenceDevice # # TODO nice path one's moved
from dexma_api_v3.factory.location_factory.location_info_factory.address import Address # TODO nice path one's moved
from dexma_api_v3.factory.base_entity import BaseEntity # TODO nice path one's moved
from dexma_api_v3.factory.custom_types.unsigned_long import UnsignedLong # TODO nice path one's moved


class Leaf(BaseEntity):

    name = StringType(required=True)
    type = StringType(required=True)
    parent =  ModelType(BaseEntity, required=True)
    area = UnsignedLong(required=True)
    summer_temp = FloatType(required=True)
    winter_temp = FloatType(required=True)
    activity = StringType(required=True)
    reference_devices = ListType(ModelType(ReferenceDevice, required=True))
    address = ModelType(Address, required=True)


