#!/usr/bin/python

# python script to search through doxygen_sqlite3.db
#
# Permission to use, copy, modify, and distribute this software and its
# documentation under the terms of the GNU General Public License is hereby
# granted. No representations are made about the suitability of this software
# for any purpose. It is provided "as is" without express or implied warranty.
# See the GNU General Public License for more details.
#

import sqlite3
import sys
import os
import getopt
import json
import re
import finder


class MemberType:
  Define="0"
  Function="1"
  Variable="2"
  Typedef="3"
  Enumeration="4"
  EnumValue="5"
  Signal="6"
  Slot="7"
  Friend="8"
  DCOP="9"
  Property="10"
  Event="11"
  File="12"

class RequestType:
  References="9901"
  Struct="9902"
  Includers="9903"
  Includees="9904"
  Members="9905"
  BaseClasses="9906"
  SubClasses="9907"

g_use_regexp=False
###############################################################################

# case-insensitive sqlite regexp function
def re_fn(expr, item):
    reg = re.compile(expr, re.I)
    return reg.search(item) is not None

def openDb(dbname):
    if dbname == None:
        dbname = "doxygen_sqlite3.db"

    if not os.path.isfile(dbname):
        raise BaseException("No such file %s" % dbname )

    conn = sqlite3.connect(dbname)
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.row_factory = sqlite3.Row
    conn.create_function("REGEXP", 2, re_fn)
    return conn

###############################################################################
def process(f,kind):
    request_processors = {
        MemberType.Function: f.function,
        MemberType.File: f.file,
        MemberType.Define:   f.macro,
        MemberType.Variable: f.variable,
        MemberType.Typedef:  f.typedef,
        RequestType.References: f.references,
        RequestType.Struct: f.struct,
        RequestType.Includers: f.includers,
        RequestType.Includees: f.includees,
        RequestType.Members: f.members,
        RequestType.BaseClasses: f.baseClasses,
        RequestType.SubClasses: f.subClasses
    }
    return request_processors[kind]()
###############################################################################
def processHref(cn,ref):
    j={}

    # is it in memberdef ?
    table="memberdef"
    if ( cn.execute("SELECT count(*) from %s WHERE refid=?"%table,[ref] ).fetchone()[0] > 0 ):
        for r in cn.execute("SELECT kind,id FROM %s WHERE refid='%s'" % (table,ref) ).fetchall():
            f=Finder(cn,r['id'],int)
            j=process(f,str(r['kind']))

    # is it in compounddef ?
    table="compounddef"
    if ( cn.execute("SELECT count(*) from %s WHERE refid=?"%table,[ref]).fetchone()[0] > 0 ):
        for r in cn.execute("SELECT id FROM %s WHERE refid=?"%table,[ref] ).fetchall():
            f=Finder(cn,r['id'],int)
            j=process(f,RequestType.Struct)

    return j
###############################################################################
def serveCgi():
    import cgi

    print 'Content-Type: application/json\n'

    fieldStorage = cgi.FieldStorage()
    form = dict((key, fieldStorage.getvalue(key)) for key in fieldStorage.keys())

    if 'href' in form:
        ref = form['href']
    else:
        print '{"result": null, "error": "no refid given"}'
        sys.exit(0)

    cn=openDb('doxygen_sqlite3.db')

    j = processHref(cn,ref)

    print json.dumps({"result":j,"error":None})
###############################################################################
def usage():
  print >>sys.stderr,"""Usage: search.py [Options]
Options:
    -h, --help
    -d <D>    Use database <D> for queries.
    -f <F>    Search for definition of function <F>.
    -m <M>    Search for definition of macro <M>.
    -r <F>    Search for references to function <F>.
    -t <T>    Search for definition of type <T>.
    -v <V>    Search for definition of variable <V>.
    -I <I>    What files are including <I>.
    -i <i>    What files are included by <i>.
    -B <C>    Get the base classes of class <C>.
    -M <C>    Get all members of class <C>.
    -S <C>    Get the sub classes of class <C>.
    -R        Consider the search <term> to be a regex.
"""
###############################################################################
def serveCli(argv):
    try:
        opts, args = getopt.getopt(argv, "hr:RI:i:d:f:m:t:v:H:M:B:S:F:",["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    ref=None
    dbname=None
    j={}
    global g_use_regexp

    for a, o in opts:
        if a in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif a in ('-d'):
            dbname=o
            continue
        elif a in ('-r'):
            kind=RequestType.References
        elif a in ('-R'):
            g_use_regexp=True
            continue
        elif a in ('-I'):
            kind=RequestType.Includers
        elif a in ('-i'):
            kind=RequestType.Includees
        elif a in ('-M'):
            kind=RequestType.Members
        elif a in ('-B'):
            kind=RequestType.BaseClasses
        elif a in ('-S'):
            kind=RequestType.SubClasses
        elif a in ('-f'):
            kind=MemberType.Function
        elif a in ('-F'):
            kind=MemberType.File
        elif a in ('-m'):
            kind=MemberType.Define
        elif a in ('-t'):
            kind=MemberType.Typedef
        elif a in ('-v'):
            kind=MemberType.Variable
        elif a in ('-H'):
            ref = o

        cn=openDb(dbname)
        f=Finder(cn,o)
        if ref != None:
          j=processHref(cn,ref)
        else:
          j=process(f,kind)
        print json.dumps(j,indent=4)


def main(argv):
    if 'REQUEST_METHOD' in os.environ:
        serveCgi()
    else:
        serveCli(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
