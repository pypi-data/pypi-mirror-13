#!/usr/bin/env python3
"""
A lib to parse and modify bini-files

------------------------------------
The parsed bini is a tuple:

bini = (int,[section])
section = (str,[entry])
entry = (str,[value])
value = int | float | string
------------------------------------

Example:

def negateEmpathy(b):
    version, sections = b
    for section in sections:
        secname, entries = section
        for entry in entries:
            entryname, values = entry
            if entryname == "empathy_rate":
                values[1] *= -1
    return b

if __name__ == "__main__":
    b = readBini("empathy.ini")
    writeIni("empathy.ini.txt", b)
    writeBini("empathy2.ini", negateEmpathy(b))
    print(biniToStr(b))

"""
from functools import reduce as _reduce
from struct import pack as _pack
from struct import unpack as _unpack

def _nub(ls):
    rs = []
    for x in ls:
        if not x in rs:
            rs.append(x)
    return rs

def _concat(iterable):
    return _reduce(lambda a,b: a+b,iterable)


#========= IO ============


def _readBinFile(p):
    with open(p,"rb") as f:
        return f.read()

def _writeFile(path,c):
    f = open(path, "w")
    f.write(c)
    f.close()

def _writeBinFile(path,c):
    f = open(path, "wb")
    f.write(c)
    f.close()

def _getOffset(table, offset):
    return str(table[offset:]).split("\\x00")[0].replace("b'","")


def _parseVal(f,strtable):
    typ, bstr = _unpack("<B", f.read(1))[0], f.read(4)
    if typ == 1: return _unpack("<i", bstr)[0]
    elif typ == 2: return _unpack("<f", bstr)[0]
    elif typ == 3: return _getOffset(strtable, _unpack("<i", bstr)[0])
    raise Exception("Unknown bini-type!("+str(typ)+")")


def _parseEntry(f, strtable):
    offset = _unpack("<H", f.read(2))[0] #bstr2shortle(f.read(2))
    num = _unpack("<B", f.read(1))[0] #hex2int(bstr2hexLe(f.read(1)))
    name = _getOffset(strtable,offset)
    entries = [_parseVal(f,strtable) for i in range(num)]
    return (name,entries)


def _parseSection(f, strtable):
    offset = _unpack("<H", f.read(2))[0] #bstr2shortle(f.read(2))
    num = _unpack("<H", f.read(2))[0] #hex2int(bstr2hexLe(f.read(2)))
    name = _getOffset(strtable,offset)
    entries = [_parseEntry(f,strtable) for i in range(num)]
    return (name,entries)


def readBini(path):
    """
    read a bini-file and parse it into its abstract representation
    """
    with open(path,"rb") as f:
        if f.read(4)!=b"BINI": raise Exception("Not a bini-file!")
        version = _unpack("<i", f.read(4))[0]
        strtableoffset = _unpack("<i", f.read(4))[0]
        strtable = _readBinFile(path)[strtableoffset:]
        secs = []
        while strtableoffset > f.tell():
            secs.append(_parseSection(f,strtable))
        return (version,secs)


def _entry2str(entry):
    return entry[0]+" = "+", ".join(map(str,entry[1]))

def biniToStr(bini):
    """
    creates a string from the bini-representation
    """
    secs = bini[1]
    return _concat(("["+t[0]+"]\n"+"\n".join(map(_entry2str,t[1]))+"\n\n" for t in secs))

#============= Building the bini-bstr ================

def _createDict(strs):
    d = {}
    offset = 0
    for s in strs:
        d[s] = offset
        offset += len(s)+1
    return d

def _str2bstr(s):
    return bytes(s,"ascii")

def _section2bstr(d, t):
    secname, entries = t
    offset = d[secname] #2
    num = len(entries)  #2
    header = _pack("<HH", offset, num)
    entriesBstr = b"".join(map(lambda v: _entry2bstr(d,v), entries))
    return header + entriesBstr

def _entry2bstr(d, t):
    offset = d[t[0]] #2
    num = len(t[1])  #1
    header = _pack("<HB", offset, num)
    values = b"".join(map(lambda v: _val2bstr(d,v),t[1]))
    return header+values

def _val2bstr(d, v):
    t = type(v)
    if t==int: return _pack("<Bi", 1, v)
    elif t==float: return _pack("<Bf", 2, v)
    elif t==str: return _pack("<Bi", 3, d[v])


def _bini2strs(bini):
    secs = bini[1]
    secnames = [n for n, ls in secs]
    entries = _concat([entries for n, entries in secs])
    entrynames = [ x[0] for x in entries ]
    values = filter(lambda x: type(x)==str ,_concat([vals for n, vals in entries]))
    return _nub(secnames+entrynames+list(values))




def _bini2bstr(bini):
    """
    bini2bstr :: Bini -> bytes
    """
    version, sections = bini
    strs = _bini2strs(bini)
    table = b"\x00".join(map(_str2bstr,strs))
    d = _createDict(strs)
    body = b""
    for sec in sections:
        body += _section2bstr(d, sec)
    strtableoffset = 12+len(body)
    header = _str2bstr("BINI")+_pack("<ii",version, strtableoffset)
    if len(header) != 12:
        print("header-len ", len(header))
        raise Exception("Defect header created!")
    return header + body + table



#=================== public =================================

def writeBini(path, bini):
    """
    create a bini-file using its abstract representation
    """
    _writeBinFile(path, _bini2bstr(bini))

def writeIni(path, bini):
    """
    create an ini-file using the bini's abstract representation
    """
    _writeFile(path, biniToStr(bini))







