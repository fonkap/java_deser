import struct

h = lambda s: ' '.join('%.2X' % ord(x) for x in s)  # format as hex

p = lambda s: (struct.unpack('>b', s)[0] if len(s) == 1 else
               struct.unpack('>h', s)[0] if len(s) == 2 else
               struct.unpack('>l', s)[0] if len(s) == 4 else
               struct.unpack('>q', s)[0])

q = lambda s,l: (struct.pack('>b', s) if l == 1 else
                 struct.pack('>h', s) if l == 2 else
                 struct.pack('>l', s) if l == 4 else
                 struct.pack('>q', s))

qu = lambda s,l: (struct.pack('>B', s) if l == 1 else
                 struct.pack('>H', s) if l == 2 else
                 struct.pack('>L', s) if l == 4 else
                 struct.pack('>Q', s))

ts = lambda s,l: p(qu(s,l))

def read_string(f):
    l = p(f.read(2))
    dat = f.read(l)
    str = dat.decode('utf-8')
    return str

def write_string(f, s):
    ba = s.encode('utf-8')
    f.write(q(len(ba), 2))
    f.write(ba)