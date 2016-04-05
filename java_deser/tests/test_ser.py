import binascii
from unittest import TestCase

from ser import *


def check_obj(expected, objs):
    out = StringIO.StringIO()
    serial(out, objs)
    result = binascii.hexlify(out.getvalue())
    assert expected == result, result


class TestSerializer(TestCase):


    def test_tcp_endpoint(self):
        out = StringIO.StringIO()
        obj = {u'host': u'dummyhost.com', u'_name': u'TCPEndpoint', u'port': 1190, u'_cls': {u'fields': [[u'host', u'L', u'String;'], [u'port', u'I', u'']], u'flags': u'\x02', u'parent': None, u'_name': u'TCPEndpoint'}}
        serial_tcp_endpoint_hp(out, obj)
        result = binascii.hexlify(out.getvalue())
        assert '000d64756d6d79686f73742e636f6d000004a6' == result, result

    def test_uid(self):
        out = StringIO.StringIO()
        obj = {u'count': 4, u'_name': u'UID', u'unique': 2, u'_cls': {u'fields': [[u'unique', u'I', u''], [u'time', u'J', u''], [u'count', u'S', u'']], u'flags': u'\x02', u'parent': None, u'_name': u'UID'}, u'time': 3}
        serial_uid(out, obj)
        result = binascii.hexlify(out.getvalue())
        assert '0000000200000000000000030004' == result, result

        out = StringIO.StringIO()
        obj = {u'count': -32714, u'_name': u'UID', u'unique': -1274474957, u'_cls': {u'fields': [[u'unique', u'I', u''], [u'time', u'J', u''], [u'count', u'S', u'']], u'flags': u'\x02', u'parent': None, u'_name': u'UID'}, u'time': 1457014483154L}
        serial_uid(out, obj)
        result = binascii.hexlify(out.getvalue())
        assert 'b4090e33000001533cd4a8d28036' == result, result

    def test_objid(self):
        out = StringIO.StringIO()
        obj = {u'_name': u'ObjID', u'space': {u'count': 4, u'_name': u'UID', u'unique': 2, u'_cls': {u'fields': [[u'unique', u'I', u''], [u'time', u'J', u''], [u'count', u'S', u'']], u'flags': u'\x02', u'parent': None, u'_name': u'UID'}, u'time': 3}, u'_cls': {u'fields': [[u'objNum', u'J', u''], [u'space', u'L', u'UID']], u'flags': u'\x02', u'parent': None, u'_name': u'ObjID'}, u'objNum': 1}
        serial_objid(out, obj)
        result = binascii.hexlify(out.getvalue())
        assert '00000000000000010000000200000000000000030004' == result, result

    def test_unicast_ref(self):
        out = StringIO.StringIO()
        obj = {u'_name': u'UnicastRef', u'endpoint': {u'host': u'dummyhost.com', u'_name': u'TCPEndpoint', u'port': 1190, u'_cls': {u'fields': [[u'host', u'L', u'String;'], [u'port', u'I', u'']], u'flags': u'\x02', u'parent': None, u'_name': u'TCPEndpoint'}}, u'objId': {u'_name': u'ObjID', u'space': {u'count': 4, u'_name': u'UID', u'unique': 2, u'_cls': {u'fields': [[u'unique', u'I', u''], [u'time', u'J', u''], [u'count', u'S', u'']], u'flags': u'\x02', u'parent': None, u'_name': u'UID'}, u'time': 3}, u'_cls': {u'fields': [[u'objNum', u'J', u''], [u'space', u'L', u'UID']], u'flags': u'\x02', u'parent': None, u'_name': u'ObjID'}, u'objNum': 1}, u'_cls': {u'fields': [[u'endpoint', u'L', u'TCPEndpoint'], [u'objId', u'L', u'ObjID']], u'flags': u'\x02', u'parent': None, u'_name': u'UnicastRef'}}
        serial_unicast_ref(out, obj)
        result = binascii.hexlify(out.getvalue())
        assert '000d64756d6d79686f73742e636f6d000004a60000000000000001000000020000000000000003000400' == result, result

    def test_ser_obj(self):
        check_obj('74000a746573745f7374725f31', ['test_str_1'])
        check_obj('70', [None])
        check_obj('737200136e662e636f2e666f6e6b2e6a6d782e4f626a302df1a90076ee6e9a0200007870'
                  , [{u'_cls': {u'fields': [], u'_uid': 3310613020554456730L, u'flags': u'\x02', u'parent': None, u'_name': u'nf.co.fonk.jmx.Obj0'}, u'_name': u'nf.co.fonk.jmx.Obj0'}])
        check_obj('737200136e662e636f2e666f6e6b2e6a6d782e4f626a31d6c8d9303c77af8d0200014900066669656c6431787000000000'
                  , [{u'field1': 0, u'_cls': {u'fields': [[u'field1', u'I', u'']], u'_uid': -2969885153054707827L, u'flags': u'\x02', u'parent': None, u'_name': u'nf.co.fonk.jmx.Obj1'}, u'_name': u'nf.co.fonk.jmx.Obj1'}])
        check_obj('757200165b4c6e662e636f2e666f6e6b2e6a6d782e4f626a303bf56691d3922a94d0020000787000000001737200136e662e636f2e666f6e6b2e6a6d782e4f626a302df1a90076ee6e9a0200007870'
                  , [{u'data': [{u'_cls': {u'fields': [], u'_uid': 3310613020554456730L, u'flags': u'\x02', u'parent': None, u'_name': u'nf.co.fonk.jmx.Obj0'}, u'_name': u'nf.co.fonk.jmx.Obj0'}], u'_cls': {u'fields': [], u'_uid': -763762748916329264L, u'flags': u'\x02', u'parent': None, u'_name': u'[Lnf.co.fonk.jmx.Obj0;'}, u'_name': u'[Lnf.co.fonk.jmx.Obj0;'}])
        check_obj('737200136e662e636f2e666f6e6b2e6a6d782e4f626a320493733d505ec7020200014c00066669656c64317400154c6e662f636f2f666f6e6b2f6a6d782f4f626a313b787070'
                  , [{u'field1': None, u'_cls': {u'fields': [[u'field1', u'L', u'Lnf/co/fonk/jmx/Obj1;']], u'_uid': 329733904906766082L, u'flags': u'\x02', u'parent': None, u'_name': u'nf.co.fonk.jmx.Obj2'}, u'_name': u'nf.co.fonk.jmx.Obj2'}])
        check_obj('757200185b4c6a6176612e726d692e7365727665722e4f626a49443b871300b8d02c647e020000787000000001737200156a6176612e726d692e7365727665722e4f626a4944a75efa128ddce55c0200024a00066f626a4e756d4c000573706163657400154c6a6176612f726d692f7365727665722f5549443b787011b42f2d498a4ba5737200136a6176612e726d692e7365727665722e5549440f12700dbf364f12020003530005636f756e744a000474696d65490006756e6971756578708001000001533cd4a8d2b4090e33'
                  , [{u'data': [{u'_name': u'java.rmi.server.ObjID', u'space': {u'count': -32767, u'_name': u'java.rmi.server.UID', u'unique': -1274474957, u'_cls': {u'fields': [[u'count', u'S', u''], [u'time', u'J', u''], [u'unique', u'I', u'']], u'_uid': 1086053664494604050L, u'flags': u'\x02', u'parent': None, u'_name': u'java.rmi.server.UID'}, u'time': 1457014483154L}, u'_cls': {u'fields': [[u'objNum', u'J', u''], [u'space', u'L', u'Ljava/rmi/server/UID;']], u'_uid': -6386392263968365220L, u'flags': u'\x02', u'parent': None, u'_name': u'java.rmi.server.ObjID'}, u'objNum': 1275696466006526885L}], u'_cls': {u'fields': [], u'_uid': -8713620060265225090L, u'flags': u'\x02', u'parent': None, u'_name': u'[Ljava.rmi.server.ObjID;'}, u'_name': u'[Ljava.rmi.server.ObjID;'}])

