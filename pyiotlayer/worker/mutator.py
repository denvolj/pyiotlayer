import abc



class AbstractMutator(object):
    @abc.abstractclassmethod
    def do(self, objects: list) -> list:
        pass


class Conveyor(object):
    __queue = ()
    __backqueue = ()

    def __init__(self, data):
        self.data = data

    def encapsulate(self):
        for mutator in self.__queue:
            mutator(self.data)

    def deencapsulate(self):
        for mutator in self.__backqueue:
            mutator(self.data)
