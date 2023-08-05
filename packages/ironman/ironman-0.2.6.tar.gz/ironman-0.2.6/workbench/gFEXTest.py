from ironman.hardware import HardwareManager, HardwareMap, HardwareNode
manager = HardwareManager()
manager.add(HardwareMap(file('xadc.yml').read(), 'xadc'))

from ironman.communicator import Jarvis, ComplexIO
j = Jarvis()
j.set_hardware_manager(manager)

@j.register('xadc')
class XADCController(ComplexIO):
    __base__ = "/sys/devices/soc0/amba/f8007100.adc/iio:device0/"
    __f__ = {
                0:   __base__+"in_temp0_offset",
                1:   __base__+"in_temp0_raw",
                2:   __base__+"in_temp0_scale",
                17:  __base__+"in_voltage0_vccint_raw",
                18:  __base__+"in_voltage0_vccint_scale",
                33:  __base__+"in_voltage1_vccaux_raw",
                34:  __base__+"in_voltage1_vccaux_scale",
                49:  __base__+"in_voltage2_vccbram_raw",
                50:  __base__+"in_voltage2_vccbram_scale",
                65:  __base__+"in_voltage3_vccpint_raw",
                66:  __base__+"in_voltage3_vccpint_scale",
                81:  __base__+"in_voltage4_vccpaux_raw",
                82:  __base__+"in_voltage4_vccpaux_scale",
                97:  __base__+"in_voltage5_vccoddr_raw",
                98:  __base__+"in_voltage5_vccoddr_scale",
                113: __base__+"in_voltage6_vrefp_raw",
                114: __base__+"in_voltage6_vrefp_scale",
                129: __base__+"in_voltage7_vrefn_raw",
                130: __base__+"in_voltage7_vrefn_scale"
            }

from ironman.constructs.ipbus import PacketHeaderStruct, ControlHeaderStruct
def buildResponsePacket(packet):
    data = ''
    data += PacketHeaderStruct.build(packet.struct.header)
    for transaction, response in zip(packet.struct.data, packet.response):
        data += ControlHeaderStruct.build(transaction)
        data += response.encode("hex").decode("hex")
    return data


from ironman.history import History
h = History()

from ironman.server import ServerFactory
from ironman.packet import IPBusPacket
from twisted.internet import reactor
from twisted.internet.defer import Deferred

reactor.listenUDP(8888, ServerFactory('udp', lambda: Deferred().addCallback(IPBusPacket).addCallback(j).addCallback(buildResponsePacket).addCallback(h.record)))

'''set up a web server from top level: http://imgur.com/jCQlfrm'''
# Site, an IProtocolFactory which glues a listening server port (IListeningPort) to the HTTPChannel implementation
from twisted.web.server import Site
# File, an IResource which glues the HTTP protocol implementation to the filesystem
from twisted.web.static import File
reactor.listenTCP(8000, Site(File("/")))

reactor.run()
