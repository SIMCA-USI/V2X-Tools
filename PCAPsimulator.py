# coding=utf-8

"""
String utilizado para simular PCAPs desde un módulo y que se reciban en otro como si fueran lanzados realmente.

"""

from kamene.all import *
import time
import datetime


class PCAPSimulator:
    def __init__(self, file, iface):
        self.file = file
        self.iface = iface
        self.pcap = rdpcap(file)
        self.pcks = []

    def run(self):
        while True:
            for packet in self.pcap:
                if len(packet) > 51:
                    bb = bytes(packet)
                    ts = int((datetime.datetime.now().second * 1000) % 2 ** 32)
                    p2 = int(ts).to_bytes(4, 'big')
                    p1 = bb[:38]
                    p3 = bb[42:]
                    sendp(Ether(p1 + p2 + p3), iface=self.iface)
                else:
                    sendp(Ether(bytes(packet)), iface=self.iface)

                time.sleep(1.3)

    def modify_pcap(self):
        for idx, packet in enumerate(self.pcap):
            if len(packet) > 51:
                bb = bytes(packet)
                ts = int((datetime.datetime.now().second * 1000) % 2 ** 32)
                p2 = int(ts).to_bytes(4, 'big')
                p1 = bb[:38]
                p3 = bb[42:]
                self.pcks.append(Ether(p1 + p2 + p3))
            else:
                self.pcks.append(Ether(bytes(packet)))
        wrpcap('capture_pruebas.pcap', self.pcks)


if __name__ == '__main__':
    import sys

    sim = PCAPSimulator(file=sys.argv[1], iface=sys.argv[2])
    sim.run()
