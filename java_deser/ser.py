import StringIO
import struct

from object_stream_constants import *


# TCPEndpoint.readHostPortFormat line 581
from tool import *


def serial_tcp_endpoint_hp(f, obj):
    write_string(f, obj['host'])
    f.write(q(obj['port'], 4))


# UID.read line 263
def serial_uid(f, obj):
    f.write(q(obj['unique'], 4))
    f.write(q(obj['time'], 8))
    f.write(q(obj['count'], 2))


# ObjID.read line 190
def serial_objid(f, obj):
    f.write(q(obj['objNum'], 8))
    serial_uid(f, obj['space'])


# LiveRef.read line 283
def serial_unicast_ref(f, obj, is_result_stream=0):
    serial_tcp_endpoint_hp(f, obj['endpoint'])
    serial_objid(f, obj['objId'])
    f.write(q(is_result_stream, 1))


def get_bytes(serializer_func, obj):
    out = StringIO.StringIO()
    serializer_func(out, obj)
    return out.getvalue()


def serial(f, objs):
    ser = Serializer(f)
    return ser.serial_objs(objs)


def serial_obj(f, obj):
    ser = Serializer(f)
    return ser.serial_obj(obj)


class Serializer:
    def __init__(self, f, marshall=False):
        self.f = f
        self.handles = []
        self.buffer = ''
        self.marshall = marshall
        self.customHandlers = {
            'java.rmi.server.RemoteObject': self.serial_remote_object,
            'javax.management.ObjectName': self.serial_object_name
        }

    def serial_classdesc(self, obj):
        f = self.f
        handles = self.handles
        if obj is None:
            f.write(TC_NULL)
        else:

            if not self.try_serial_handle('TC_CLASSDESC', obj):
                f.write(TC_CLASSDESC)
                write_string(f, obj['_name'])
                f.write(q(obj['_uid'], 8))
                f.write(str(obj['flags']))
                handles.append(('TC_CLASSDESC', obj))
                f.write(q(len(obj['fields']), 2))
                for field in obj['fields']:
                    name, typ, fcls = field
                    f.write(str(typ))
                    write_string(f, name)
                    if typ in 'L[':
                        self.serial_str(fcls)
                if self.marshall:
                    f.write(TC_NULL) # annotateClass - MarshalOutputStream
                f.write(TC_ENDBLOCKDATA)
                self.serial_classdesc(obj['parent'])


    def try_serial_handle(self, type, obj):
        tup = (type, obj)
        if tup in self.handles:
            handle = self.handles.index(tup) + 0x7E0000
            self.f.write(TC_REFERENCE)
            self.f.write(q(handle, 4))
            return True
        return False

    def serial_obj(self, obj):
        self.flush_buffer()
        f = self.f
        handles = self.handles
        if obj is None:
            f.write(TC_NULL)
        elif obj.__class__ == str:
            self.serial_str(obj)
        #     return data
        # elif b == '\x7E':  # ~ TC_ENUM
        #     enum = {}
        #     enum['_cls'] = parse_obj()
        #     handles.append(('TC_ENUM', enum))
        #     enum['_name'] = parse_obj()
        #     return enum
        #     if b == '\x70':   # skip 0x70 (TC_NULL)
        #         b = f.read(1)
        #     assert b == '\x78', h(b)
        #     cls['parent'] = parse_obj()
        #     return cls
        else:
            cls = obj['_cls']
            if cls['_name'].startswith('['):
                f.write(TC_ARRAY)
                self.serial_classdesc(cls)  # using class of first element as class of array
                f.write(q(len(obj['data']), 4))
                handles.append(('TC_ARRAY', obj['data']))
            #     assert cls['_name'].startswith('['), cls['_name']
                for item in obj['data']:
                    if cls['_name'] == '[B':
                        assert len(item) == 1, 'wrong item length ' + item
                        f.write(str(item))
                    elif cls['_name'] == '[Z':
                        val = item['value']
                        b = 1 if val else 0
                        f.write(q(b, 1))
                    elif cls['_name'] == '[I':
                        f.write(q(item['value'], 4))
                    else:
                        self.serial_obj(item)
            else:
                # TC_OBJECT
                f.write(TC_OBJECT)
                self.serial_classdesc(cls)
                # handle = len(handles)
                parents = [cls]
                while parents[0]['parent']:
                    parents.insert(0, parents[0]['parent'])
                handles.append(('TC_OBJECT', obj))
                for cls in parents:
                    for name, typ, fcls in cls['fields'] if cls['flags'] in ('\2', '\3') else []:
                        if typ == 'I':  # Integer
                            f.write(q(obj[name], 4))
                        elif typ == 'S':  # Short
                            f.write(q(obj[name], 2))
                        elif typ == 'J':  # Long
                            f.write(q(obj[name], 8))
                        elif typ == 'Z':  # Bool
                            b = 1 if obj[name] else 0
                            f.write(q(b, 1))
                #         elif typ == 'F':  # Float
                #             obj[name] = h(f.read(4))
                #         elif typ in 'BC':  # Byte, Char
                #             obj[name] = f.read(1)
                        elif typ in 'L[':  # Object, Array
                            self.serial_obj(obj[name])
                #         else:  # Unknown
                #             assert False, (name, typ, fcls)

                if cls['flags'] in ('\3', '\x0C'):  # SC_WRITE_METHOD, SC_BLOCKDATA
                    customHandler = self.customHandlers.get(cls['_name'])
                    if customHandler:
                        customHandler(obj['data'])
                    f.write(TC_ENDBLOCKDATA)

    def serial_str(self, obj):
        if not self.try_serial_handle('TC_STRING', obj):
            self.f.write(TC_STRING)
            write_string(self.f, obj)
            self.handles.append(('TC_STRING', obj))

    def serial_objs(self, objs):
        # magic = f.read(2)
        # assert magic == '\xAC\xED', h(magic)  # STREAM_MAGIC
        # assert p(f.read(2)) == 5  # STREAM_VERSION
        for obj in objs:
            self.serial_obj(obj)

    def write_bytes(self, bytes):
        self.buffer += bytes

    def write_int(self, value):
        self.buffer += q(value, 4)

    def write_ulong(self, value):
        self.buffer += qu(value, 8)

    def flush_buffer(self):
        if len(self.buffer) > 0:
            f = self.f
            f.write(TC_BLOCKDATA)
            f.write(q(len(self.buffer), 1))
            f.write(self.buffer)
            self.buffer = ''

    # RemoteObject.readObject line 421
    def serial_remote_object(self, obj):
        f = self.f
        write_string(f, 'UnicastRef')
        serial_unicast_ref(f, obj['ref'], 0)

    def serial_object_name(self, obj):
        self.serial_obj(obj)

