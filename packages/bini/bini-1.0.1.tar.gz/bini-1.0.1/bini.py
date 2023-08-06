#!/usr/bin/env python3
from functools import reduce
from struct import pack, unpack
"""

A lib to parse and modify bini-files

"""
#func

#magic methods
multi = lambda a,b: a*b
add = lambda a,b: a+b
div = lambda a,b: a/b
dict2func = lambda d: lambda k: d[k]

def take(n, iterable):
    i = 0
    for x in iterable:
        if i < n:
            yield x

def nub(ls):
    rs = []
    for x in ls:
        if not x in rs:
            rs.append(x)
    return rs

def head(iterable):
    for x in iterable:
        return x

def tail(iterable):
    first=True
    for i in iterable:
        if first: first=False
        else: yield i

def concat(iterable):
    return reduce(add,iterable)

def zipWith(op,ls,bs):
    return (op(t[0],t[1]) for t in zip(ls,bs))

#========= IO ============
def readBinFile(p):
    with open(p,"rb") as f:
        return f.read()

def writeFile(path,c):
    f = open(path, "w")
    f.write(c)
    f.close()

def writeBinFile(path,c):
    f = open(path, "wb")
    f.write(c)
    f.close()


#========== hex & bin==============
_char2binDict = {
    "0" : [0,0,0,0],
    "1" : [0,0,0,1],
    "2" : [0,0,1,0],
    "3" : [0,0,1,1],
    "4" : [0,1,0,0],
    "5" : [0,1,0,1],
    "6" : [0,1,1,0],
    "7" : [0,1,1,1],
    "8" : [1,0,0,0],
    "9" : [1,0,0,1],
    "a" : [1,0,1,0],
    "b" : [1,0,1,1],
    "c" : [1,1,0,0],
    "d" : [1,1,0,1],
    "e" : [1,1,1,0],
    "f" : [1,1,1,1]
}
char2bin = dict2func(_char2binDict)
hex2bin = lambda s: concat(map(char2bin, s))
bin2int = lambda b: sum(zipWith(multi, reversed(b),  [2**e for e in range(0,100)]))
hex2int = lambda s: bin2int(hex2bin(s))
def bin2float(b):
    sign = b[0]
    exp = bin2int(b[1:9])-127
    mant = 1 + sum(zipWith(div, b[10:], [2**x for x in range(1,100)]))
    return (-1 if sign==1 else 1) * mant * (2**exp)
hex2float = lambda s: bin2float(hex2bin(s))
#==================== Parsing ===================

def bstr2hexLe(bstr):
    bs = []
    for x in map(hex,reversed(bstr)):
        b = x.split("x")[1]
        if len(b)==1: b = "0"+b
        bs.append(b)
    return "".join(bs)

def bstr2int32le(bstr):
    return unpack("<i", bstr)[0]

def bstr2float32le(bstr):
    return unpack("<f", bstr)[0]

def bstr2shortle(bstr):
    return unpack("<H", bstr)[0]


def _getOffset(table, offset):
    return str(table[offset:]).split("\\x00")[0].replace("b'","")

def _parseVal(f,strtable):
    typ, bstr = hex2int(bstr2hexLe(f.read(1))), f.read(4)
    if typ == 1: return bstr2int32le(bstr)
    elif typ == 2: return bstr2float32le(bstr)
    elif typ == 3: return _getOffset(strtable, bstr2int32le(bstr))
    raise Exception("Unknown bini-type!("+str(typ)+")")

def _createParser(n, parseFunc):
    def f(f, strtable):
        offset = bstr2shortle(f.read(2))
        num = hex2int(bstr2hexLe(f.read(n)))
        name = _getOffset(strtable,offset)
        entries = [parseFunc(f,strtable) for i in range(num)]
        return (name,entries)
    return f

_parseEntry = _createParser(1,_parseVal)
_parseSection = _createParser(2,_parseEntry)

def readBini(path):
    with open(path,"rb") as f:
        if f.read(4)!=b"BINI": raise Exception("Not a bini-file!")
        version = bstr2int32le(f.read(4)) #readInt32le(f)
        strtableoffset = bstr2int32le(f.read(4)) #readInt32le(f)
        strtable = readBinFile(path)[strtableoffset:]
        secs = []
        while strtableoffset > f.tell():
            secs.append(_parseSection(f,strtable))
        return (version,secs)


def entry2str(e):
    return e[0]+" = "+", ".join(map(str,e[1]))

def bini2str(bini):
    secs = bini[1]
    return concat(("["+t[0]+"]\n"+"\n".join(map(entry2str,t[1]))+"\n\n" for t in secs))

#============= Building the bini-bstr ================

def bini2strs(bini):
    secs = bini[1]
    secnames = [n for n, ls in secs]
    entries = concat([entries for n, entries in secs])
    entrynames = [ x[0] for x in entries ]
    values = filter(lambda x: type(x)==str ,concat([vals for n, vals in entries]))
    return nub(secnames+entrynames+list(values))

def _createDict(strs):
    d = {}
    offset = 0
    for s in strs:
        d[s] = offset
        offset += len(s)+1
    return d

def str2bstr(s):
    return bytes(s,"ascii")

def section2bstr(d, t):
    secname, entries = t
    offset = d[secname] #2
    num = len(entries)  #2 1
    header = pack("<HH", offset, num)
    entriesBstr = b"".join(map(lambda v: entry2bstr(d,v), entries))
    return header + entriesBstr

def entry2bstr(d, t):
    offset = d[t[0]] #2
    num = len(t[1])  #1
    header = pack("<HB", offset, num)
    values = b"".join(map(lambda v: val2bstr(d,v),t[1]))
    return header+values

def val2bstr(d, v):
    t = type(v)
    if t==int: return pack("<Bi", 1, v)
    elif t==float: return pack("<Bf", 2, v)
    elif t==str: return pack("<Bi", 3, d[v])

def bini2bstr(bini):
    version, sections = bini
    strs = bini2strs(bini)
    table = b"\x00".join(map(str2bstr,strs))
    d = _createDict(strs)
    body = b""
    for sec in sections:
        body += section2bstr(d, sec)
    strtableoffset = 12+len(body)
    header = str2bstr("BINI")+pack("<ii",version, strtableoffset)
    if len(header) != 12:
        print("header-len ", len(header))
        raise Exception("Defect header created!")
    return header + body + table


