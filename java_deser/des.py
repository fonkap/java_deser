"""
Java deserializer
adapted from StackOverflow response: http://stackoverflow.com/a/16470856/3324704
"""
import StringIO
import struct

from object_stream_constants import *

h = lambda s: ' '.join('%.2X' % ord(x) for x in s)  # format as hex
p = lambda s: (struct.unpack('>b', s)[0] if len(s) == 1 else
               struct.unpack('>h', s)[0] if len(s) == 2 else
               struct.unpack('>l', s)[0] if len(s) == 4 else
               struct.unpack('>q', s)[0])


# p = lambda s: sum(ord(x) * 256 ** i for i, x in enumerate(reversed(s)))  # parse integer
def read_string(f):
    l = p(f.read(2))
    dat = f.read(l)
    str = dat.decode('utf-8')
    return str


#TCPEndpoint.readHostPortFormat line 581
def parse_tcp_endpoint_hp(f):
    obj = {'_cls': {
        'fields': [('host', 'L', 'String;'), ('port', 'I', '')],
        '_name': 'TCPEndpoint',
        'flags': '\x02',
        'parent': None,
    }}
    obj['_name'] = obj['_cls']['_name']
    obj['host'] = read_string(f)
    obj['port'] = p(f.read(4))
    return obj


#UID.read line 263
def parse_uid(f):
    obj = {'_cls': {'fields': [['count', 'S', ''], ['time', 'J', ''], ['unique', 'I', '']], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}}
    obj['_name'] = obj['_cls']['_name']
    obj['unique'] = p(f.read(4))
    obj['time'] = p(f.read(8))
    obj['count'] = p(f.read(2))
    return obj


#ObjID.read line 190
def parse_objid(f):
    obj = {'_cls': {
        'fields': [('objNum', 'J', ''), ('space', 'L', 'Ljava/rmi/server/UID;')],
        '_name': 'java.rmi.server.ObjID',
        '_uid': 12060351809741186396L,
        'flags': '\x02',
        'parent': None,
    }}
    obj['_name'] = obj['_cls']['_name']
    obj['objNum'] = p(f.read(8))
    obj['space'] = parse_uid(f)
    return obj


#LiveRef.read line 283
def parse_unicast_ref(f):
    obj = {'_cls': {
        'fields': [('endpoint', 'L', 'TCPEndpoint'), ('objId', 'L', 'ObjID')],
        '_name': 'UnicastRef',
        'flags': '\x02',
        'parent': None,
    }}
    obj['_name'] = obj['_cls']['_name']
    obj['endpoint'] = parse_tcp_endpoint_hp(f)
    obj['objId'] = parse_objid(f)
    f.read(1) #isResultStream
    return obj


def parse(f):
    des = Deserializer(f)
    return des.parse_objs()


class Deserializer:
    def __init__(self, f):
        self.f = f
        self.handles = []
        self.unread = 0
        self.customHandlers = {
            'java.rmi.server.RemoteObject': self.parse_remote_object,
            'javax.management.ObjectName': self.parse_object_name
        }

    def parse_obj(self):
        f = self.f
        handles = self.handles
        b = f.read(1)
        if not b:
            raise StopIteration  # not necessarily the best thing to throw here.
        if b == TC_NULL:  # p TC_NULL
            return None
        elif b == TC_REFERENCE:  # q TC_REFERENCE
            handle = p(f.read(4)) - 0x7E0000  # baseWireHandle
            o = handles[handle]
            return o[1]
        elif b == TC_STRING:  # t TC_STRING
            string = f.read(p(f.read(2))).decode('utf-8')
            handles.append(('TC_STRING', string))
            return string
        elif b == TC_ARRAY:  # u TC_ARRAY
            data = []
            obj = {}
            cls = self.parse_obj()
            obj['_cls'] = cls
            obj['_name'] = obj['_cls']['_name']
            size = p(f.read(4))
            handles.append(('TC_ARRAY', data))
            assert cls['_name'].startswith('['), cls['_name']
            for x in range(size):
                if cls['_name'] in ('[B', '[I'):
                    data.append(f.read({'[B': 1, '[I': 4}[cls['_name']]))
                else:
                    data.append(self.parse_obj())
            obj['data'] = data
            return obj
        elif b == TC_ENUM:  # ~ TC_ENUM
            enum = {}
            enum['_cls'] = self.parse_obj()
            handles.append(('TC_ENUM', enum))
            enum['_name'] = self.parse_obj()
            return enum
        elif b == TC_CLASSDESC:  # r TC_CLASSDESC
            cls = {'fields': []}
            full_name = f.read(p(f.read(2)))
            # cls['_name'] = full_name.split('.')[-1]  # i don't care about full path
            cls['_name'] = full_name
            cls['_uid'] = p(f.read(8))  # uid
            cls['flags'] = f.read(1)
            handles.append(('TC_CLASSDESC', cls))
            assert cls['flags'] in ('\2', '\3', '\x0C', '\x12'), h(cls['flags'])
            b = f.read(2)
            for i in range(p(b)):
                typ = f.read(1)
                name = f.read(p(f.read(2)))
                fcls = self.parse_obj() if typ in 'L[' else ''
                # cls['fields'].append((name, typ, fcls.split('/')[-1]))  # don't care about full path
                cls['fields'].append((name, typ, fcls))
            b = f.read(1)
            if b == TC_NULL:   # skip 0x70 (TC_NULL)
                b = f.read(1)
            assert b == TC_ENDBLOCKDATA, h(b)
            cls['parent'] = self.parse_obj()
            return cls
        # TC_OBJECT
        assert b == TC_OBJECT, (h(b), h(f.read(4)), repr(f.read(50)))
        obj = {}
        obj['_cls'] = self.parse_obj()
        obj['_name'] = obj['_cls']['_name']
        handle = len(handles)
        parents = [obj['_cls']]
        while parents[0]['parent']:
            parents.insert(0, parents[0]['parent'])
        handles.append(('TC_OBJECT', obj))
        for cls in parents:
            for name, typ, fcls in cls['fields'] if cls['flags'] in ('\2', '\3') else []:
                if typ == 'I':  # Integer
                    obj[name] = p(f.read(4))
                elif typ == 'S':  # Short
                    obj[name] = p(f.read(2))
                elif typ == 'J':  # Long
                    obj[name] = p(f.read(8))
                elif typ == 'Z':  # Bool
                    b = f.read(1)
                    assert p(b) in (0, 1)
                    obj[name] = bool(p(b))
                elif typ == 'F':  # Float
                    obj[name] = h(f.read(4))
                elif typ in 'BC':  # Byte, Char
                    obj[name] = f.read(1)
                elif typ in 'L[':  # Object, Array
                    obj[name] = self.parse_obj()
                else:  # Unknown
                    assert False, (name, typ, fcls)
            if cls['flags'] in ('\3', '\x0C'):  # SC_WRITE_METHOD, SC_BLOCKDATA
                customHandler = self.customHandlers.get(cls['_name'])
                if customHandler:
                    obj['data'] = customHandler()
                else:
                    b = f.read(1)
                    if b == TC_BLOCKDATA:  # see the readObject / writeObject methods
                        block = f.read(p(f.read(1)))
                        if cls['_name'].endswith('HashMap') or cls['_name'].endswith('Hashtable'):
                            # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/HashMap.java.html
                            # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/Hashtable.java.html
                            assert len(block) == 8, h(block)
                            size = p(block[4:])
                            obj['data'] = []  # python doesn't allow dicts as keys
                            for i in range(size):
                                k = self.parse_obj()
                                v = self.parse_obj()
                                obj['data'].append((k, v))
                            try:
                                obj['data'] = dict(obj['data'])
                            except TypeError:
                                pass  # non hashable keys
                        elif cls['_name'].endswith('HashSet'):
                            # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/HashSet.java.html
                            assert len(block) == 12, h(block)
                            size = p(block[-4:])
                            obj['data'] = []
                            for i in range(size):
                                obj['data'].append(self.parse_obj())
                        elif cls['_name'].endswith('ArrayList'):
                            # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/ArrayList.java.html
                            assert len(block) == 4, h(block)
                            obj['data'] = []
                            for i in range(obj['size']):
                                obj['data'].append(self.parse_obj())
                        else:
                            assert False, cls['_name']

                b = f.read(1)
                assert b == TC_ENDBLOCKDATA, h(b) + ' ' + repr(f.read(30))  # TC_ENDBLOCKDATA
        handles[handle] = ('py', obj)
        return obj

    def parse_objs(self):
        # magic = f.read(2)
        # assert magic == '\xAC\xED', h(magic)  # STREAM_MAGIC
        # assert p(f.read(2)) == 5  # STREAM_VERSION
        objs = []
        while 1:
            try:
                objs.append(self.parse_obj())
            except StopIteration:
                return objs

    def read_long(self):
        self.check_reading_block();
        l = 8
        self.unread -= l
        assert self.unread >= 0
        return p(self.f.read(l))

    def check_reading_block(self):
        if self.unread == 0:
            b = self.f.read(1)
            assert TC_BLOCKDATA == b, 'unexpected byte in block header ' + h(b)
            self.unread = p(self.f.read(1))

    #RemoteObject.readObject line 421
    def parse_remote_object(self):
        f = self.f
        obj = {'_cls': {
            'fields': [('ref', 'L', 'UnicastRef')],
            '_name': 'RemoteObject',
            'flags': '\x02',
            'parent': None,
        }}
        b = f.read(1)
        assert TC_BLOCKDATA == b, 'bad value ' + h(b)
        block = f.read(p(f.read(1)))
        fb = StringIO.StringIO(block)
        obj['_name'] = obj['_cls']['_name']
        refClassName = read_string(fb)
        assert refClassName == 'UnicastRef'
        obj['ref'] = parse_unicast_ref(fb)
        return obj

    def parse_object_name(self):
        f = self.f
        pos = f.tell()
        b = f.read(1)
        assert TC_STRING == b, 'bad value ' + h(b)
        f.seek(pos)
        return self.parse_obj()
