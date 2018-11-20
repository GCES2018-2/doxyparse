import sys
# from search import search.MemberType 
import search

class Finder:
    def __init__(self,cn,name,row_type=str):
        self.cn=cn
        self.name=name
        self.row_type=row_type

    def match(self,row):
        if self.row_type is int:
            return " id=?"
        else:
            if search.g_use_regexp == True:
                return " REGEXP (?,%s)" %row
            else:
                return " %s=?" %row

    def fileName(self,id_file):
        if self.cn.execute("SELECT COUNT(*) FROM files WHERE rowid=?",[id_file]).fetchone()[0] > 1:
            print >>sys.stderr,"WARNING: non-uniq fileid [%s]. Considering only the first match." % id_file

        for r in self.cn.execute("SELECT * FROM files WHERE rowid=?",[id_file]).fetchall():
                return r['name']

        return ""

    def fileId(self,name):
        if self.cn.execute("SELECT COUNT(*) FROM files WHERE"+self.match("name"),[name]).fetchone()[0] > 1:
            print >>sys.stderr,"WARNING: non-uniq file name [%s]. Considering only the first match." % name

        for r in self.cn.execute("SELECT rowid FROM files WHERE"+self.match("name"),[name]).fetchall():
                return r[0]

        return -1
###############################################################################
    def references(self):
        o=[]
        cur = self.cn.cursor()
        cur.execute("SELECT refid FROM memberdef WHERE"+self.match("name"),[self.name])
        refids = cur.fetchall()

        if len(refids) == 0:
            return o

        refid = refids[0]['refid']
        cur = self.cn.cursor()
        #TODO:SELECT rowid from refids where refid=refid
        for info in cur.execute("SELECT * FROM xrefs WHERE refid_dst LIKE '%"+refid+"%'"):
            item={}
            cur = self.cn.cursor()
            for i2 in cur.execute("SELECT * FROM memberdef WHERE refid=?",[info['src']]):
                item['name']=i2['name']
                item['src']=info['src']
                item['file']=self.fileName(info['id_file'])
                item['line']=info['line']

            o.append(item)
        return o
###############################################################################
    def function(self):
        o=[]
        c=self.cn.execute('SELECT * FROM memberdef WHERE'+self.match("name")+' AND kind=?',[self.name,search.MemberType.Function])
        for r in c.fetchall():
            item={}
            item['name'] = r['name']
            item['definition'] = r['definition']
            item['argsstring'] = r['argsstring']
            item['file'] = self.fileName(r['id_file'])
            item['line'] = r['line']
            item['detaileddescription'] = r['detaileddescription']
            o.append(item)
        return o
###############################################################################
    def file(self):
        o=[]
        for r in self.cn.execute("SELECT rowid,* FROM files WHERE"+self.match("name"),[self.name]).fetchall():
            item={}
            item['name'] = r['name']
            item['id'] =   r['rowid']
            o.append(item)
        return o

###############################################################################
    def macro(self):
        o=[]
        c=self.cn.execute('SELECT * FROM memberdef WHERE'+self.match("name")+' AND kind=?',[self.name,search.MemberType.Define])
        for r in c.fetchall():
            item={}
            item['name'] = r['name']
            if r['argsstring']:
                item['argsstring'] = r['argsstring']
            item['definition'] = r['initializer']
            item['file'] = self.fileName(r['id_file'])
            item['line'] = r['line']
            o.append(item)
        return o
###############################################################################
    def typedef(self):
        o=[]
        c=self.cn.execute('SELECT * FROM memberdef WHERE'+self.match("name")+' AND kind=?',[self.name,search.MemberType.Typedef])
        for r in c.fetchall():
            item={}
            item['name'] = r['name']
            item['definition'] = r['definition']
            item['file'] = self.fileName(r['id_file'])
            item['line'] = r['line']
            o.append(item)
        return o
###############################################################################
    def variable(self):
        o=[]
        c=self.cn.execute('SELECT * FROM memberdef WHERE'+self.match("name")+' AND kind=?',[self.name,search.MemberType.Variable])
        for r in c.fetchall():
            item={}
            item['name'] = r['name']
            item['definition'] = r['definition']
            item['file'] = self.fileName(r['id_file'])
            item['line'] = r['line']
            o.append(item)
        return o
###############################################################################
    def params(self):
        o=[]
        c=self.cn.execute('SELECT id FROM memberdef WHERE'+self.match("name"),[self.name])
        for r in c.fetchall():
            #a=("SELECT * FROM params where id=(SELECT id_param FROM memberdef_params where id_memberdef=?",[id_memberdef])
            item={}
            item['id'] = r['id']
            o.append(item)
        return o
###############################################################################
    def struct(self):
        o=[]
        c=self.cn.execute('SELECT * FROM compounddef WHERE'+self.match("name"),[self.name])
        for r in c.fetchall():
            item={}
            item['name'] = r['name']
            o.append(item)
        return o
###############################################################################
    def includers(self):
        o=[]
        fid = self.fileId(self.name)
        c=self.cn.execute('SELECT * FROM includes WHERE id_dst=?',[fid])
        for r in c.fetchall():
            item={}
            item['name'] = self.fileName(r['id_src'])
            o.append(item)
        return o
###############################################################################
    def includees(self):
        o=[]
        fid = self.fileId(self.name)
        c=self.cn.execute('SELECT * FROM includes WHERE id_src=?',[fid])
        for r in c.fetchall():
            item={}
            item['name'] = self.fileName(r['id_dst'])
            o.append(item)
        return o
###############################################################################
    def members(self):
        o=[]
        c=self.cn.execute('SELECT * FROM memberdef WHERE'+self.match("scope"),[self.name])
        for r in c.fetchall():
            item={}
            item['name'] = r['name']
            item['definition'] = r['definition']
            item['argsstring'] = r['argsstring']
            item['file'] = self.fileName(r['id_file'])
            item['line'] = r['line']
            #item['documentation'] = r['documentation']
            o.append(item)
        return o
###############################################################################
    def baseClasses(self):
        o=[]
        c=self.cn.execute('SELECT base FROM basecompoundref WHERE'+self.match("derived"),[self.name])
        for r in c.fetchall():
            item={}
            item['name'] = r['base']
            o.append(item)
        return o
###############################################################################
    def subClasses(self):
        o=[]
        c=self.cn.execute('SELECT derived FROM basecompoundref WHERE'+self.match("base"),[self.name])
        for r in c.fetchall():
            item={}
            item['name'] = r['derived']
            o.append(item)
        return o