from __future__ import print_function
import io
import sys
import logging
import xml.etree.ElementTree as ET


_log = logging.getLogger(__name__)

def open_xmp_file(filename):
    return open(filename, 'r+b')

def find_xmp_packets(stream):
    captures = []
    capturing = None

    for line in stream:
        if '<?xpacket end=' in line:
            capturing = None

        if capturing is not None:
            if len(captures) - 1 < capturing:
                _log.debug('Creating new capture {0}'.format(capturing))
                captures.append([])

            captures[capturing].append(line)

        if '<?xpacket begin=' in line:
            if capturing is not None:
                _log.error('Found an XMP packet begin header while already'
                           ' capturing. Things will break.')

            capturing = len(captures)
            _log.debug('Found XMP packet: {0}'.format(capturing))

    packets = []

    for capture in captures:
        packets.append('\n'.join(capture))

    return packets

def extract(filename):
    xmp_file = open_xmp_file(filename)

    xmp_packets = find_xmp_packets(xmp_file)

    if len(xmp_packets) > 1:
        _log.warning('Found more than one XMP packet, using the first packet')

    root = ET.fromstring(xmp_packets[0])

    tracks = root.findall(
        './{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'
        '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'
        '/{http://ns.adobe.com/xap/1.0/mm/}Pantry'
        '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'
        '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li'
        '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'
        '/{http://ns.adobe.com/xmp/1.0/DynamicMedia/}Tracks')

    _log.debug('tracks: {!r}'.format(tracks))

    layers = []

    for track in tracks:
        meta = track.findall(
            './{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'
            '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li'
            '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'
            '/{http://ns.adobe.com/xmp/1.0/DynamicMedia/}markers'
            '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Seq'
            '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li'
            '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'
            '/{http://ns.adobe.com/xmp/1.0/DynamicMedia/}cuePointParams'
            '/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Seq'
            '/*')

        if not meta:
            continue

        _log.debug('track meta: {!r}'.format(meta))

        layer_data = {}

        for datapair in meta:
            # datapair is a rdf:li element
            key = datapair.attrib.get('{http://ns.adobe.com/xmp/1.0/DynamicMedia/}key')
            value = datapair.attrib.get('{http://ns.adobe.com/xmp/1.0/DynamicMedia/}value')

            _log.debug('key: {!r}, value: {!r}'.format(key, value))

            layer_data.update({
                key: value})

        layers.append(layer_data)

    return layers


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    import glob
    files = []

    for arg in sys.argv[1:]:
        for filename in glob.glob(arg):
            files.append(filename)

    for f in files:
        for layer in extract(f):
            if 'position' in layer:
                x, y, z = [int(float(i)) for i in layer['position'].split(',')]

                layer.update({
                    'x': x,
                    'y': y
                })
            else:
                _log.error('File {0} does not have a position attribute'.format(
                    f))

                layer.update({
                    'x': 'NA',
                    'y': 'NA'
                })

            if 'fillColor' in layer:
                r, g, b = [
                    int(float(i) * 255) for i in layer['fillColor'].split(',')]

                layer.update({
                    'r': r,
                    'g': g,
                    'b': b
                })
                layer['hexcolor'] = '#{r:0>2x}{g:0>2x}{b:0>2x}'.format(
                    **layer).upper()
            else:
                _log.error('File {0} does not have a fillColor attribute'.format(
                    f))
                layer.update({
                    'r': 'NA',
                    'g': 'NA',
                    'b': 'NA'
                })
                layer['hexcolor'] = '#MISSING'

            for prop in ['fontSize', 'font']:
                if not prop in layer:
                    _log.error('File {0} does not have a {1} attribute.'.format(
                        f,
                        prop))
                    layer[prop] = None
            print('{0}:'.format(f))
            print('{x};{y};0;{fontSize};{font};{hexcolor};0;%%xmllookup:menypriser:MenuItem:ItemID:ItemPriceIn:1252+%%;0;0;0;0;0;0;0;0;0;0;;0;;0;'.format(
                **layer))
            print('')

