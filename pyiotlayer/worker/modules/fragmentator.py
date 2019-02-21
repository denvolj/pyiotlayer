import abc
import base64
import random

from pyiotlayer.worker.mutator import AbstractMutator
from pyiotlayer.objects import IotBaseObject, IotContainer, IotObject, IotDatum
from pyiotlayer.utils import IotUtils


class BaseFragmentator(AbstractMutator):
    def __init__(self, data:IotBaseObject, mtu=450):
        self.iot_object = data
        self.mtu = mtu
        self.size = IotUtils.getSize(self.iot_object)
        self.empty = IotUtils.getSize(self.iot_object, False)

    def new(self, data:IotBaseObject, mtu=450):
        return type(self)(data, mtu)

    def compose(self, parts):
        result = []
        for pack in parts:
            fragments = self.buildBlock(pack)
            result += fragments
        return result

    def buildBlock(self, fragments):
        result = []
        new_object = self.iot_object.clone(False)
        for id, pack in enumerate(fragments):
            if IotUtils.getSize(new_object) + IotUtils.getSize(pack) <= self.mtu:
                new_object.append(pack)
            else:
                new_object.set("count", len(fragments))
                new_object.set("passed", id)
                result.append(new_object)
                new_object = self.iot_object.clone(False)

        new_object.set("count", len(fragments))
        new_object.set("passed", id)
        result.append(new_object)

        return result


class ContainerFragmentator(BaseFragmentator):
    __bytes_reserved = 16           # reserving bytes for field length (objects count/passed)

    def do(self):
        if self.size <= self.mtu:
            # No fragmentation need
            return [self.iot_object]

        # Fragmentation required
        object_fragments = []
        objects = self.iot_object.get("content")
        for object_ in objects:
            # Max possible content length
            object_mtu = self.mtu-self.empty-ContainerFragmentator.__bytes_reserved

            # Sets of objects. Each set in separated container
            object_fragments += [ObjectFragmentator(object_, object_mtu).do()]

        result = self.compose(object_fragments)
        return result


class ObjectFragmentator(BaseFragmentator):
    __bytes_reserved = 16           # reserving bytes for field length (datums count/passed)
    def do(self):
        if self.size <= self.mtu:
            # No fragmentation need
            return [self.iot_object]

        datums = self.iot_object.get("content")
        result = []
        for datum in datums:
            object_mtu = self.mtu-self.empty-ObjectFragmentator.__bytes_reserved
            result += [DatumFragmentator(datum, object_mtu).do()]
        
        return self.compose(result)


class DatumFragmentator(BaseFragmentator):
    __fragsize = 50
    def do(self):
        if self.size <= self.mtu:
            # No fragmentation need
            return [self.iot_object]

        json_string = IotUtils.toJSON(self.iot_object)
        base64_string = base64.standard_b64encode(json_string.encode('UTF-8')).decode('ascii')
        
        raw_fragments = []
        while base64_string:
            raw_fragments.append(base64_string[:DatumFragmentator.__fragsize])
            base64_string = base64_string[DatumFragmentator.__fragsize:]

        fragments = []
        new_did = random.randrange(1, 9999)
        for chunk in raw_fragments:
            iot_object = IotDatum({
                "did": new_did,
                "ed": chunk,
            })
            fragments.append(iot_object)

        return fragments

