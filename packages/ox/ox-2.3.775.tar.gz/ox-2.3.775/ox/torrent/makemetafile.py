# Written by Bram Cohen
# multitracker extensions by John Hoffman
# see LICENSE.txt for license information

from os.path import getsize, split, join, abspath, isdir
from os import listdir
from hashlib import sha1 as sha
from copy import copy
import re

from six import PY2
if PY2:
    from .bencode import bencode
else:
    from .bencode3 import bencode
from threading import Event
from time import time
from traceback import print_exc
try:
    from sys import getfilesystemencoding
    ENCODING = getfilesystemencoding()
except:
    from sys import getdefaultencoding
    ENCODING = getdefaultencoding()

defaults = [
    ('announce_list', '',
        'a list of announce URLs - explained below'),
    ('httpseeds', '',
        'a list of http seed URLs - explained below'),
    ('piece_size_pow2', 0,
        "which power of 2 to set the piece size to (0 = automatic)"),
    ('comment', '',
        "optional human-readable comment to put in .torrent"),
    ('filesystem_encoding', '',
        "optional specification for filesystem encoding " +
        "(set automatically in recent Python versions)"),
    ('target', '',
        "optional target file for the torrent")
    ]

default_piece_len_exp = 18

ignore = ['core', 'CVS']

def print_announcelist_details():
    print ('    announce_list = optional list of redundant/backup tracker URLs, in the format:')
    print ('           url[,url...][|url[,url...]...]')
    print ('                where URLs separated by commas are all tried first')
    print ('                before the next group of URLs separated by the pipe is checked.')
    print ("                If none is given, it is assumed you don't want one in the metafile.")
    print ('                If announce_list is given, clients which support it')
    print ('                will ignore the <announce> value.')
    print ('           Examples:')
    print ('                http://tracker1.com|http://tracker2.com|http://tracker3.com')
    print ('                     (tries trackers 1-3 in order)')
    print ('                http://tracker1.com,http://tracker2.com,http://tracker3.com')
    print ('                     (tries trackers 1-3 in a randomly selected order)')
    print ('                http://tracker1.com|http://backup1.com,http://backup2.com')
    print ('                     (tries tracker 1 first, then tries between the 2 backups randomly)')
    print ('')
    print ('    httpseeds = optional list of http-seed URLs, in the format:')
    print ('            url[|url...]')

reg = re.compile(r'^[^/\\.~][^/\\]*$')

def is_number(value):
    return isinstance(value, int) or isinstance(value,float)


def check_info(info):
    if not isinstance(info, dict):
        raise ValueError('bad metainfo - not a dictionary')
    pieces = info.get('pieces')
    if not isinstance(pieces, bytes) or len(pieces) % 20 != 0:
        raise ValueError('bad metainfo - bad pieces key')
    piecelength = info.get('piece length')
    if not is_number(piecelength) or piecelength <= 0:
        raise ValueError('bad metainfo - illegal piece length')
    name = info.get('name')
    if not isinstance(name, bytes):
        raise ValueError('bad metainfo - bad name')
    if not reg.match(name.decode('utf-8')):
        raise ValueError('name %s disallowed for security reasons' % name)
    if ('files' in info) == ('length' in info):
        raise ValueError('single/multiple file mix')
    if 'length' in info:
        length = info.get('length')
        if not is_number(length) or length < 0:
            raise ValueError('bad metainfo - bad length')
    else:
        files = info.get('files')
        if not isinstance(files, list):
            raise ValueError
        for f in files:
            if not isinstance(f, dict):
                raise ValueError('bad metainfo - bad file value')
            length = f.get('length')
            if not is_number(length) or length < 0:
                raise ValueError('bad metainfo - bad length')
            path = f.get('path')
            if not isinstance(path, list) or path == []:
                raise ValueError('bad metainfo - bad path')
            for p in path:
                if not isinstance(p, bytes):
                    raise ValueError('bad metainfo - bad path dir')
                if not reg.match(p.decode('utf-8')):
                    raise ValueError('path %s disallowed for security reasons' % p)
        for i in range(len(files)):
            for j in range(i):
                if files[i]['path'] == files[j]['path']:
                    raise ValueError('bad metainfo - duplicate path')
    
def make_meta_file(file, url, params = {}, flag = Event(),
                   progress = lambda x: None, progress_percent = 1):
    if 'piece_size_pow2' in params:
        piece_len_exp = params['piece_size_pow2']
    else:
        piece_len_exp = default_piece_len_exp
    if 'target' in params and params['target'] != '':
        f = params['target']
    else:
        a, b = split(file)
        if b == '':
            f = a + '.torrent'
        else:
            f = join(a, b + '.torrent')
            
    if piece_len_exp == 0:  # automatic
        size = calcsize(file)
        if   size > 8*1024*1024*1024:   # > 8 gig =
            piece_len_exp = 21          #   2 meg pieces
        elif size > 2*1024*1024*1024:   # > 2 gig =
            piece_len_exp = 20          #   1 meg pieces
        elif size > 512*1024*1024:      # > 512M =
            piece_len_exp = 19          #   512K pieces
        elif size > 64*1024*1024:       # > 64M =
            piece_len_exp = 18          #   256K pieces
        elif size > 16*1024*1024:       # > 16M =
            piece_len_exp = 17          #   128K pieces
        elif size > 4*1024*1024:        # > 4M =
            piece_len_exp = 16          #   64K pieces
        else:                           # < 4M =
            piece_len_exp = 15          #   32K pieces
    piece_length = 2 ** piece_len_exp

    encoding = None
    if 'filesystem_encoding' in params:
        encoding = params['filesystem_encoding']
    if not encoding:
        encoding = ENCODING
    if not encoding:
        encoding = 'ascii'
    
    info = makeinfo(file, piece_length, encoding, flag, progress, progress_percent)
    if flag.isSet():
        return
    check_info(info)
    h = open(f.encode(encoding), 'wb')
    data = {'info': info, 'announce': url.strip(), 'creation date': int(time())}
    
    if 'comment' in params and params['comment']:
        data['comment'] = params['comment']
        
    if 'real_announce_list' in params:    # shortcut for progs calling in from outside
        data['announce-list'] = params['real_announce_list']
    elif 'announce_list' in params and params['announce_list']:
        l = []
        for tier in params['announce_list'].split('|'):
            l.append(tier.split(','))
        data['announce-list'] = l
        
    if 'real_httpseeds' in params:    # shortcut for progs calling in from outside
        data['httpseeds'] = params['real_httpseeds']
    elif 'httpseeds' in params and params['httpseeds']:
        data['httpseeds'] = params['httpseeds'].split('|')

    if 'url-list' in params and params['url-list']:
        data['url-list'] = params['url-list'].split('|')

    if 'playtime' in params and params['playtime']:
        data['info']['playtime'] = params['playtime']

    h.write(bencode(data))
    h.close()

def calcsize(file):
    if not isdir(file):
        return getsize(file)
    total = 0
    for s in subfiles(abspath(file)):
        total += getsize(s[1])
    return total


def uniconvertl(l, e):
    r = []
    try:
        for s in l:
            r.append(uniconvert(s, e))
    except UnicodeError:
        raise UnicodeError('bad filename: '+join(*l))
    return r

def uniconvert(s, e):
    try:
        if isinstance(s, bytes):
            s = s.decode(e)
    except UnicodeError:
        raise UnicodeError('bad filename: '+s)
    return s.encode('utf-8')

def makeinfo(file, piece_length, encoding, flag, progress, progress_percent=1):
    file = abspath(file)
    if isdir(file):
        subs = subfiles(file)
        subs.sort()
        pieces = []
        sh = sha()
        done = 0
        fs = []
        totalsize = 0.0
        totalhashed = 0
        for p, f in subs:
            totalsize += getsize(f)

        for p, f in subs:
            pos = 0
            size = getsize(f)
            fs.append({'length': size, 'path': uniconvertl(p, encoding)})
            h = open(f, 'rb')
            while pos < size:
                a = min(size - pos, piece_length - done)
                sh.update(h.read(a))
                if flag.isSet():
                    return
                done += a
                pos += a
                totalhashed += a
                
                if done == piece_length:
                    pieces.append(sh.digest())
                    done = 0
                    sh = sha()
                if progress_percent:
                    progress(totalhashed / totalsize)
                else:
                    progress(a)
            h.close()
        if done > 0:
            pieces.append(sh.digest())
        return {'pieces': b''.join(pieces),
            'piece length': piece_length, 'files': fs, 
            'name': uniconvert(split(file)[1], encoding) }
    else:
        size = getsize(file)
        pieces = []
        p = 0
        h = open(file, 'rb')
        while p < size:
            x = h.read(min(piece_length, size - p))
            if flag.isSet():
                return
            pieces.append(sha(x).digest())
            p += piece_length
            if p > size:
                p = size
            if progress_percent:
                progress(float(p) / size)
            else:
                progress(min(piece_length, size - p))
        h.close()
        return {'pieces': b''.join(pieces), 
            'piece length': piece_length, 'length': size, 
            'name': uniconvert(split(file)[1], encoding) }

def subfiles(d):
    r = []
    stack = [([], d)]
    while len(stack) > 0:
        p, n = stack.pop()
        if isdir(n):
            for s in listdir(n):
                if s not in ignore and s[:1] != '.':
                    stack.append((copy(p) + [s], join(n, s)))
        else:
            r.append((p, n))
    return r


def completedir(dir, url, params = {}, flag = Event(),
                vc = lambda x: None, fc = lambda x: None):
    files = listdir(dir)
    files.sort()
    ext = '.torrent'
    if 'target' in params:
        target = params['target']
    else:
        target = ''

    togen = []
    for f in files:
        if f[-len(ext):] != ext and (f + ext) not in files:
            togen.append(join(dir, f))
        
    total = 0
    for i in togen:
        total += calcsize(i)

    subtotal = [0]
    def callback(x, subtotal = subtotal, total = total, vc = vc):
        subtotal[0] += x
        vc(float(subtotal[0]) / total)
    for i in togen:
        fc(i)
        try:
            t = split(i)[-1]
            if t not in ignore and t[0] != '.':
                if target != '':
                    params['target'] = join(target,t+ext)
                make_meta_file(i, url, params, flag, progress = callback, progress_percent = 0)
        except ValueError:
            print_exc()
