from unittest import TestCase

import binascii

from des import *


def check_obj(expected, str):
    inp = StringIO.StringIO(binascii.unhexlify(str))
    par = parse(inp)
    assert expected == par, par

class TestDeserializer(TestCase):
    def test_tcp_endpoint(self):
        inp = StringIO.StringIO(binascii.unhexlify('000d64756d6d79686f73742e636f6d000004a6'))
        tcp_endpoint_hp = parse_tcp_endpoint_hp(inp)
        expected = {'port': 1190, 'host': u'dummyhost.com', '_cls': {'fields': [('host', 'L', 'String;'), ('port', 'I', '')], 'flags': '\x02', 'parent': None, '_name': 'TCPEndpoint'}, '_name': 'TCPEndpoint'}
        assert expected == tcp_endpoint_hp, tcp_endpoint_hp

    def test_uid(self):
        inp = StringIO.StringIO(binascii.unhexlify('0000000200000000000000030004'))
        uid = parse_uid(inp)
        expected = {'time': 3, 'count': 4, 'unique': 2, '_cls': {'fields': [['count', 'S', ''], ['time', 'J', ''], ['unique', 'I', '']], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}
        assert expected == uid, uid
        inp = StringIO.StringIO(binascii.unhexlify('b4090e33000001533cd4a8d28036'))
        uid = parse_uid(inp)
        expected = {'time': 1457014483154L, 'count': -32714, 'unique': -1274474957, '_cls': {'fields': [['count', 'S', ''], ['time', 'J', ''], ['unique', 'I', '']], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}
        assert expected == uid, uid

    def test_objid(self):
        inp = StringIO.StringIO(binascii.unhexlify('00000000000000010000000200000000000000030004'))
        objid = parse_objid(inp)
        expected = {'objNum': 1, 'space': {'time': 3, 'count': 4, 'unique': 2, '_cls': {'fields': [['count', 'S', ''], ['time', 'J', ''], ['unique', 'I', '']], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}, '_cls': {'fields': [('objNum', 'J', ''), ('space', 'L', 'Ljava/rmi/server/UID;')], '_uid': -6386392263968365220, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.ObjID'}, '_name': 'java.rmi.server.ObjID'}
        assert expected == objid, objid

    def test_unicast_ref(self):
        inp = StringIO.StringIO(binascii.unhexlify('000d64756d6d79686f73742e636f6d000004a60000000000000001000000020000000000000003000400'))
        ref = parse_unicast_ref(inp)
        expected = {'objId': {'objNum': 1, 'space': {'time': 3, 'count': 4, 'unique': 2, '_cls': {'fields': [['count', 'S', ''], ['time', 'J', ''], ['unique', 'I', '']], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}, '_cls': {'fields': [('objNum', 'J', ''), ('space', 'L', 'Ljava/rmi/server/UID;')], '_uid': -6386392263968365220, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.ObjID'}, '_name': 'java.rmi.server.ObjID'}, 'endpoint': {'port': 1190, 'host': u'dummyhost.com', '_cls': {'fields': [('host', 'L', 'String;'), ('port', 'I', '')], 'flags': '\x02', 'parent': None, '_name': 'TCPEndpoint'}, '_name': 'TCPEndpoint'}, '_cls': {'fields': [('endpoint', 'L', 'TCPEndpoint'), ('objId', 'L', 'ObjID')], 'flags': '\x02', 'parent': None, '_name': 'UnicastRef'}, '_name': 'UnicastRef'}
        assert expected == ref, ref

    def test_rmi_server_impl_stub(self):
        inp = StringIO.StringIO(binascii.unhexlify('7372002e6a617661782e6d616e6167656d656e742e72656d6f74652e726d692e524d49536572766572496d706c5f5374756200000000000000020200007872001a6a6176612e726d692e7365727665722e52656d6f746553747562e9fedcc98be1651a0200007872001c6a6176612e726d692e7365727665722e52656d6f74654f626a656374d361b4910c61331e03000078707736000a556e6963617374526566000d64756d6d79686f73742e636f6d000004a6000000000000000100000002000000000000000300040078'))
        stub = parse(inp)
        expected = [{'data': {'ref': {'objId': {'objNum': 1, 'space': {'time': 3, 'count': 4, 'unique': 2, '_cls': {'fields': [['count', 'S', ''], ['time', 'J', ''], ['unique', 'I', '']], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}, '_cls': {'fields': [('objNum', 'J', ''), ('space', 'L', 'Ljava/rmi/server/UID;')], '_uid': -6386392263968365220, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.ObjID'}, '_name': 'java.rmi.server.ObjID'}, 'endpoint': {'port': 1190, 'host': u'dummyhost.com', '_cls': {'fields': [('host', 'L', 'String;'), ('port', 'I', '')], 'flags': '\x02', 'parent': None, '_name': 'TCPEndpoint'}, '_name': 'TCPEndpoint'}, '_cls': {'fields': [('endpoint', 'L', 'TCPEndpoint'), ('objId', 'L', 'ObjID')], 'flags': '\x02', 'parent': None, '_name': 'UnicastRef'}, '_name': 'UnicastRef'}, '_cls': {'fields': [('ref', 'L', 'UnicastRef')], 'flags': '\x02', 'parent': None, '_name': 'RemoteObject'}, '_name': 'RemoteObject'}, '_cls': {'fields': [], '_uid': 2, 'flags': '\x02', 'parent': {'fields': [], '_uid': -1585587260594494182L, 'flags': '\x02', 'parent': {'fields': [], '_uid': -3215090123894869218L, 'flags': '\x03', 'parent': None, '_name': 'java.rmi.server.RemoteObject'}, '_name': 'java.rmi.server.RemoteStub'}, '_name': 'javax.management.remote.rmi.RMIServerImpl_Stub'}, '_name': 'javax.management.remote.rmi.RMIServerImpl_Stub'}]
        assert expected == stub, stub

    def test_object_name(self):
        inp = StringIO.StringIO(binascii.unhexlify('7372001b6a617661782e6d616e6167656d656e742e4f626a6563744e616d650f03a71beb6d15cf030000707870740012464f4f3a6e616d653d48656c6c6f4265616e78'))
        obj_name = parse(inp)
        expected = [{'data': u'FOO:name=HelloBean', '_cls': {'fields': [], '_uid': 1081892073854801359L, 'flags': '\x03', 'parent': None, '_name': 'javax.management.ObjectName'}, '_name': 'javax.management.ObjectName'}]
        assert expected == obj_name, obj_name

    def test_des_obj(self):
        check_obj([u'test_str_1'], '74000a746573745f7374725f31')
        check_obj([None], '70')
        check_obj([{'_cls': {'fields': [], '_uid': 3310613020554456730L, 'flags': '\x02', 'parent': None, '_name': 'nf.co.fonk.jmx.Obj0'}, '_name': 'nf.co.fonk.jmx.Obj0'}]
                  , '737200136e662e636f2e666f6e6b2e6a6d782e4f626a302df1a90076ee6e9a0200007870')
        check_obj([{'field1': 0, '_cls': {'fields': [('field1', 'I', '')], '_uid': -2969885153054707827L, 'flags': '\x02', 'parent': None, '_name': 'nf.co.fonk.jmx.Obj1'}, '_name': 'nf.co.fonk.jmx.Obj1'}]
                  , '737200136e662e636f2e666f6e6b2e6a6d782e4f626a31d6c8d9303c77af8d0200014900066669656c6431787000000000')
        check_obj([{'_cls': {'fields': [('value', 'B', '')], '_uid': -7183698231559129828L, 'flags': '\x02', 'parent': {'fields': [], '_uid': -8742448824652078965L, 'flags': '\x02', 'parent': None, '_name': 'java.lang.Number'}, '_name': 'java.lang.Byte'}, 'value': '\x00', '_name': 'java.lang.Byte'}]
                  , '7372000e6a6176612e6c616e672e427974659c4e6084ee50f51c02000142000576616c7565787200106a6176612e6c616e672e4e756d62657286ac951d0b94e08b020000787000')
        check_obj([{'data': [{'_cls': {'fields': [], '_uid': 3310613020554456730L, 'flags': '\x02', 'parent': None, '_name': 'nf.co.fonk.jmx.Obj0'}, '_name': 'nf.co.fonk.jmx.Obj0'}], '_cls': {'fields': [], '_uid': -763762748916329264L, 'flags': '\x02', 'parent': None, '_name': '[Lnf.co.fonk.jmx.Obj0;'}, '_name': '[Lnf.co.fonk.jmx.Obj0;'}]
                  , '757200165b4c6e662e636f2e666f6e6b2e6a6d782e4f626a303bf56691d3922a94d0020000787000000001737200136e662e636f2e666f6e6b2e6a6d782e4f626a302df1a90076ee6e9a0200007870')
        check_obj([{'field1': None, '_cls': {'fields': [('field1', 'L', u'Lnf/co/fonk/jmx/Obj1;')], '_uid': 329733904906766082L, 'flags': '\x02', 'parent': None, '_name': 'nf.co.fonk.jmx.Obj2'}, '_name': 'nf.co.fonk.jmx.Obj2'}]
                  , '737200136e662e636f2e666f6e6b2e6a6d782e4f626a320493733d505ec7020200014c00066669656c64317400154c6e662f636f2f666f6e6b2f6a6d782f4f626a313b787070')
        check_obj([{'objNum': 1275696466006526885L, 'space': {'count': -32767, 'unique': -1274474957, 'time': 1457014483154L, '_cls': {'fields': [('count', 'S', ''), ('time', 'J', ''), ('unique', 'I', '')], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}, '_cls': {'fields': [('objNum', 'J', ''), ('space', 'L', u'Ljava/rmi/server/UID;')], '_uid': -6386392263968365220L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.ObjID'}, '_name': 'java.rmi.server.ObjID'}]
                  , '737200156a6176612e726d692e7365727665722e4f626a4944a75efa128ddce55c0200024a00066f626a4e756d4c000573706163657400154c6a6176612f726d692f7365727665722f5549443b787011b42f2d498a4ba5737200136a6176612e726d692e7365727665722e5549440f12700dbf364f12020003530005636f756e744a000474696d65490006756e6971756578708001000001533cd4a8d2b4090e33')
        check_obj([{'data': [{'objNum': 1275696466006526885L, 'space': {'count': -32767, 'unique': -1274474957, 'time': 1457014483154L, '_cls': {'fields': [('count', 'S', ''), ('time', 'J', ''), ('unique', 'I', '')], '_uid': 1086053664494604050L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.UID'}, '_name': 'java.rmi.server.UID'}, '_cls': {'fields': [('objNum', 'J', ''), ('space', 'L', u'Ljava/rmi/server/UID;')], '_uid': -6386392263968365220L, 'flags': '\x02', 'parent': None, '_name': 'java.rmi.server.ObjID'}, '_name': 'java.rmi.server.ObjID'}], '_cls': {'fields': [], '_uid': -8713620060265225090L, 'flags': '\x02', 'parent': None, '_name': '[Ljava.rmi.server.ObjID;'}, '_name': '[Ljava.rmi.server.ObjID;'}]
                  , '757200185b4c6a6176612e726d692e7365727665722e4f626a49443b871300b8d02c647e020000787000000001737200156a6176612e726d692e7365727665722e4f626a4944a75efa128ddce55c0200024a00066f626a4e756d4c000573706163657400154c6a6176612f726d692f7365727665722f5549443b787011b42f2d498a4ba5737200136a6176612e726d692e7365727665722e5549440f12700dbf364f12020003530005636f756e744a000474696d65490006756e6971756578708001000001533cd4a8d2b4090e33')


