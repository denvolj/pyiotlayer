import abc
import copy


class AbstractNestedClass(object):
    _links = {}
    _proto = {}
    _protoobject = None

    def __init__(self, data:dict):
        self._data = copy.deepcopy(self._proto)
        self._data.update(data)


    def get(self, name, default=None):
        return self._data.get(self.linker(name), default)

    def set(self, name, value):
        self._data[self.linker(name)] = value

    def getval(self, name, default=None):
        return self._data.get(name, default)

    def setval(self, name, value):
        self._data[name] = value

    @abc.abstractclassmethod
    def childClass(cls):
        """
        Define child element type
        Must return class of child elements (or None if there is no childs)
        """
        return None

    @classmethod
    def linker(cls, name):
        link = cls._links[name]
        return link

    @classmethod
    def prototype(cls):
        return cls({})


class IotBaseObject(AbstractNestedClass):
    _proto = None

    def __init__(self, data={}):
        super().__init__(data=data)

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
            iot_object.count = len(data)
            iot_object.passed = key+1
            result.append(iot_object)

        return result

    @classmethod
    def parseSingleObject(cls, data: dict, deep=True):
        iot_object = cls(data)
        if iot_object.childClass() is not None:
            parsedchilds = []
            if not deep:
                parsedchilds = iot_object.prototype().get("content")
            else:
                childs = iot_object.get("content")
                parsedchilds = iot_object.childClass().parse(childs)
            iot_object.set("content", parsedchilds)

        return iot_object

    def clone(self, deep: bool = True):
        # Option "deep" defines rule for content
        # Not for other nested objects
        cloned_object = copy.deepcopy(self)

        if not deep:
            proto_content = self.prototype().get("content")
            cloned_object.set("content", proto_content)

        return cloned_object

    def validate(self) -> bool:
        proto = self.prototype()
        
        for key, defvalue in vars(proto).iteritems():
            if defvalue is None and getattr(self, key) is None:
                return False

        return True

    def append(self, data):
        if isinstance(data, IotBaseObject):
            if not isinstance(data, self.childClass()):
                raise ValueError("Value is not an instance of child class")

            # All OK, we got all what we needed
            self.get("content").append(data)

        elif isinstance(data, dict):
            # Dictionary! Try parse it as child and retry
            child = self.childClass().parse(data)
            self.append(child)

        elif isinstance(data, list):
            # Probably, we got array of IotObjects, try each of them
            for obj in data:
                self.append(obj)

        else:
            # I tried...
            raise TypeError("Can't append unsupported value")



class IotContainer(IotBaseObject):
    _proto = {
            "mid": None,
            "o": [],
            "oc": 1,
            "op": 1,
            "src": "",
            "dst": ""
        }

    _links = {
            "content": "o",
            "id": "mid",
            "count": "oc",
            "passed": "op",
            "source": "src",
            "destination": "dst"
        }

    @classmethod
    def childClass(cls):
        return IotObject


class IotObject(IotBaseObject):
    _proto = {
            "oid": None,
            "ot": None,
            "d": [],
            "dc": 1,
            "dp": 1,
            "src": "",
            "dst": ""
        }

    _links = {
            "id": "oid",
            "type": "ot",
            "content": "d",
            "count": "dc",
            "passed": "dp",
            "source": "src",
            "destination": "dst"
        }

    @classmethod
    def childClass(cls):
        return IotDatum


class IotDatum(IotBaseObject):
    _proto = {
            "did": "",
            "bc": 0,
            "bp": 0,
            "ed": "",
            "src": "",
            "dst": ""
        }
        
    _links = {
            "content": "ed",
            "id": "did",
            "count": "bc",
            "passed": "bp",
            "source": "src",
            "destination": "dst"
        }

    @classmethod
    def childClass(cls):
        return None
