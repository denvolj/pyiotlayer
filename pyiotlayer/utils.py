import json

from pyiotlayer.objects import IotBaseObject, IotContainer, IotObject, IotDatum

class IotUtils(object):

    # Производит минимизацию структуры:
    # - Убирает ключи-значения, соответствующие значению по умолчанию
    # - Заменяет [{..}] на {..}
    @classmethod
    def minify(cls, IotBaseObject):
        pass

    @classmethod
    def getIotClassType(cls, data):
        class_types = (
            IotContainer,
            IotObject,
            IotDatum
        )

        for iot_class in class_types:
            if iot_class.parseSingleObject(data, False).validate():
                return iot_class

        return None

    @classmethod
    def getSize(cls, obj, deep=True):
        tmp_object = obj.clone(deep)
        length = len(IotUtils.toJSON(tmp_object))
        del(tmp_object)
        return length

    @classmethod
    def fromJSON(cls, string: str) -> IotBaseObject:
        json_object = json.loads(string)
        iot_object = IotContainer.parse(json_object)

        return iot_object

    @classmethod
    def toJSON(cls, iot_object: IotBaseObject) -> object:
        # Cloning object to avoid it modification
        cloned_object = iot_object.clone()
        content = cloned_object.get("content")

        # Minify data due specification requirement: [{...}] -> {...}
        if isinstance(content, list) and len(content) == 1:
            cloned_object.set("content", content[0])

        return json.dumps(cloned_object, separators=(',',':'), default=lambda o: o._data)
    

"""

root = IotBuilder(
    IotContainer()
        .set("content", [])
        .set("content", [])
        .set("content", [])
        .set("content", [])

    ])
)



"""


