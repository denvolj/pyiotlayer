import json

from pyiotlayer.transport.objects import IotBaseObject, IotContainer


class IotJsonUtil(object):
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
            cloned_object[cloned_object.linker("content")] = content[0]

        return json.dumps(cloned_object, separators=(',',':'), default=lambda o: o._data)


class IotBuilder(object):
    # Производит минимизацию структуры:
    # - Убирает ключи-значения, соответствующие значению по умолчанию
    # - Заменяет [{..}] на {..}
    @classmethod
    def minify(cls, IotBaseObject):
        pass

    # Определить какой класс у переданной стуктуры
    @classmethod
    def getIotClassType(cls, data: dict):
        pass

    def __init__(self, data: IotBaseObject):
        self.__data = data

    def getSize(self, without_content=False):
        tmp_object = self.__data.clone(without_content)
        return len(IotJsonUtil.toJSON(tmp_object))

    def append(self, data):
        if isinstance(data, IotBaseObject):
            # All OK, we got all what we needed
            self.__data.get("content").append(data)
        
        elif isinstance(data, dict):
            # Dictionary! Try parse it as child and retry
            child = self.__data.childClass().parse(data)
            self.append(child)

        elif isinstance(data, list):
            # Probably, we got array of IotObjects, try each of them
            for obj in enumerate(data):
                self.append(obj)

        elif isinstance(data, str):
            # Oh, a string! Maybe we can parse it as JSON?..
            json_data = IotJsonUtil.fromJSON(str)
            self.append(json_data)

        else:
            # I tried...
            raise TypeError("Can't append unsupported value")

    

"""

root = IotBuilder().parse(jsonstring)



"""


