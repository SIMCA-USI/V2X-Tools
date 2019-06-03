#V2X-Tools
Conjunto de herramientas útiles relacionadas con los módulos, como el script de 
instalación o el simulador de PCAPs.

##installation.py
Script utilizado para instalar la iso base en un módulo. Para lanzarlo:

`sudo python3 installation.py -i <ruta de la iso> -o <ruta donde está montada la CF> -id <id del módulo>`

En cuanto a la ruta donde está montada la Compact Flash, normalmente será 
/dev/sdc o /dev/sdd, según los pendrives u otros dispositivos que están conectados
al ordenador. Es posible que, incluso seleccionando bien la ruta, al terminar el 
proceso de instalación aparezca algún problema con una ruta temporal del sistema.
Suele ocurrir si se ha realizado el proceso de instalación en varias tarjetas una 
detrás de otra. Para solucionarlo, es conveniente reiniciar el ordenador.

##diagnostic.py

Script utilizado para comprobar el estado de un módulo, borrando automáticamente
logs antiguos, poniendo la fecha correcta en caso de que se haya desconfigurado
y lanzando el jar de AUTOCITS. Para lanzarlo:

`python3 diagnostic.py -u <nombre del usuario> -p <contraseña>
-ip <ip del módulo> -rsa <ruta de la clave RSA>` 

Normalmente, bastará con indicar el parámetro de IP ya que, por defecto, el 
usuario y contraseña es root:debian. El parámetro de RSA está en caso de 
necesitarla para módulos de carretera.

##PCAPsimulator

String utilizado para simular PCAPs desde un módulo y que se reciban en otro 
como si fueran lanzados realmente. Para lanzarlo:

`sudo python3 PCAPsimulator.py <ruta del PCAP> <interfaz de red>`

##coordinatesParser

Script utilizado para parsear las coordenadas de un PCAP y generar un CSV con ellas. Está en un estado muy primario,
debe mejorarse para recibir el chorro de bytes de cada paquete y decodificar cada parámetro. De esta forma, no solo
funcionaría para parsear las coordenadas. Para lanzarlo:

`sudo python3 coordinatesParser.py <ruta del PCAP>`