# -*- coding: utf-8 -*-

import json
from transit.writer import Writer
from transit.reader import Reader
from StringIO import StringIO

def transit_dumps(value):
    io = StringIO()
    writer = Writer(io, 'json')
    writer.write(value)
    return unicode(io.getvalue())

a_str = u'Av. Zañartu 1482, Ñuñoa, Santiago, Chile, 7780272'

print(transit_dumps(u'Av. Zañartu 1482, Ñuñoa, Santiago, Chile, 7780272'))
print(json.dumps(a_str, ensure_ascii=False))
#transit_dumps(u'Av. Zañartu 1482, Ñuñoa, Santiago, Chile, 7780272'.encode('utf-8'))


