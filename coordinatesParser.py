# coding=utf-8

"""
Script utilizado para parsear las coordenadas de un PCAP y generar un CSV con ellas. Está en un estado muy primario,
debe mejorarse para recibir el chorro de bytes de cada paquete y decodificar cada parámetro. De esta forma, no solo
funcionaría para parsear las coordenadas.
"""

from kamene.all import *
from struct import unpack


class PCAPSimulator:
    def __init__(self, file):
        self.file = file
        self.pcap = rdpcap(file)

    def run(self):
        with open("output.csv", "w") as f:
            for packet in self.pcap:
                if len(packet) > 51:
                    bb = bytes(packet)
                    lat = unpack('!i', bb[38:42])[0] / 10 ** 7
                    lon = unpack('!i', bb[42:46])[0] / 10 ** 7
                    f.write("{}, {}\n".format(lat, lon))
                else:
                    pass


if __name__ == '__main__':
    import sys

    sim = PCAPSimulator(file=sys.argv[1])
    sim.run()
