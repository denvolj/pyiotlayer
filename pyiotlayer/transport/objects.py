import abc
import copy


class IotAbstractObject(abc.ABC):
    @abc.abstractmethod
    def validate(self) -> bool:
        """
        Validate this IOT context
        """
        pass

    @abc.abstractclassmethod
    def childClass(cls):
        """
        Define child element type
        Must return class of child elements (or None if there is no childs)
        """
        return None

    @abc.abstractclassmethod
    def linker(cls, name) -> dict:
        """
        Define common field types of IOT objects by key-value
        """
        return {}

    @abc.abstractclassmethod
    def prototype(cls) -> dict:
        """
        Define prototype with default values.
        Mark fields as "required" with value = None.
        """
        return {}


class IotBaseObject(IotAbstractObject):
    @classmethod 
    def parse(cls, data, deep=True) -> list:
        if not isinstance(data, dict) and not isinstance(data, list):
            raise TypeError("Data must be dictionary or list")

        result = []

        # Input unification to stay DRY
        if isinstance(data, dict):
            data = [data]

        for key, value in enumerate(data):
            iot_object = cls.parseSingleObject(value, deep)
            iot_object.set("count", len(data))
            iot_object.set("passed", key+1)
            result.append(iot_object)

        return result

    @classmethod
    def parseSingleObject(cls, data: dict, deep=True):
        iot_object = cls(data)
        if iot_object.childClass() is not None:
            parsedchilds = []
            if not deep:
                default = iot_object.linker("content")
                parsedchilds = iot_object.prototype()[default]
            else:
                childs = iot_object.get("content")
                parsedchilds = iot_object.childClass().parse(childs)
            iot_object.set("content", parsedchilds)

        return iot_object


    def __init__(self, data):
        if not isinstance(data, dict):
            raise TypeError("Data must be dictionary")
        
        self.__dict__ = data

    def get(self, name, default=None):
        return getattr(self, self.linker(name), default)

    def set(self, name, value):
        setattr(self, self.linker(name), value)

    def clone(self, without_content: bool = False):
        cloned_object = copy.deepcopy(self)
        if without_content:
            cloned_object.set("content", [])

        return cloned_object

    def validate(self) -> bool:
        proto = self.prototype()
        
        for key, defvalue in proto:
            if defvalue is None and self.get(key) is None:
                return False

        return True



class IotContainer(IotBaseObject):
    @classmethod
    def linker(cls, name):
        return {
            "content": "o",
            "id": "mid",
            "count": "oc",
            "passed": "op",
            "source": "src",
            "destination": "dst"
        }[name]

    @classmethod
    def prototype(cls):
        return {
            "mid": None,
            "o": [],
            "oc": 1,
            "op": 1,
            "src": "",
            "dst": ""
        }

    @classmethod
    def childClass(cls):
        return IotObject


class IotObject(IotBaseObject):
    @classmethod
    def linker(cls, name):
        return {
            "id": "oid",
            "type": "ot",
            "content": "d",
            "count": "dc",
            "passed": "dp",
            "source": "src",
            "destination": "dst"
        }[name]

    @classmethod
    def prototype(cls):
        return {
            "oid": None,
            "ot": None,
            "d": [],
            "dc": 1,
            "dp": 1,
            "src": "",
            "dst": ""
        }

    @classmethod
    def childClass(cls):
        return IotDatum


class IotDatum(IotBaseObject):
    @classmethod
    def linker(cls, name):
        return {
            "content": "ed",
            "id": "did",
            "count": "bc",
            "passed": "bp",
            "source": "src",
            "destination": "dst"
        }[name]

    @classmethod
    def prototype(cls):
        return {
            "did": "",
            "bc": 0,
            "bp": 0,
            "ed": "",
            "src": "",
            "dst": ""
        }