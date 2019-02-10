from pyiotlayer.transport.objects import IotContainer

iotproto = {
    "mid": 1,
    "o": [
        {
            "oid": 128,
            "d": [
                {
                    "longdata": ""
                },
                {
                    "longdata": ""
                },
                {
                    "longdata": ""
                },
            ]
        }, 
        {
            "oid": 129,
            "d": [
                {
                    "longdata": ""
                },
                {
                    "longdata": ""
                },
                {
                    "longdata": ""
                },
            ]
        }
    ]
}

# ToDo: исправить проблему с высчитыванием passed/count

class Fragmentator(object):
    GlobalMTU = 450
    @classmethod
    def do(cls, container):
        fragments = []
        objects = container.clone().get("content")
        cur_container = container.clone(True)

        cursor = 0
        while len(objects):
            cur_object = objects[cursor]
            if cur_object.getSize() + container.getSize(True) > Fragmentator.GlobalMTU:
                # Произвести фрагментацию объекта
                pass

            elif cur_object.getSize() + cur_container.getSize() <= Fragmentator.GlobalMTU:
                cur_container.addChild(cur_object)
                del objects[cursor]
                cursor = 0
            
            if cursor >= len(objects)-1:
                fragments.append(cur_container)
                if len(objects):
                    cur_container = container.cloneEmpty()
                    continue
                else:
                    break
            else:
                cursor += 1

        return fragments






if __name__ == '__main__':
    container = IotContainer.parse(iotproto)[0]
    Fragmentator.do(container)