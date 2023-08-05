import os
import sys
import stat
import time
import hashlib
import psutil
import six

#from os.path import isfile, isdir, join

import okerrclient.taskseq as ts

if six.PY2:
    # old 2.x python
    class PermissionError(Exception):
        pass
    class FileNotFoundError(Exception):
        pass


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


class FsTaskProcessor(ts.TaskProcessor):
    chapter = 'Filesystem'

class DirProc(FsTaskProcessor):
    help='filesystem subtree'
    defconf={'path': '', 'md5': '', 'sha1': '', 'sha256': '', 'mindepth': '0', 'maxdepth': '10'}

    def getrec(self, path, args, depth):
        # print("! getrec:",path)
        out = []

        
        try:
            rec=dict()
            rec['path']=os.path.realpath(path)
            rec['basename']=os.path.basename(path)
            rec['type']="UNKNOWN"
            rec['depth']=depth

            s = os.lstat(path)

            rec['size']=s.st_size
            rec['atime']=int(s.st_atime)
            rec['ctime']=int(s.st_ctime)
            rec['mtime']=int(s.st_mtime)
            
            now = time.time()
            rec['aage']=int(now-s.st_atime)
            rec['mage']=int(now-s.st_mtime)
            rec['cage']=int(now-s.st_ctime)
            

            
            if stat.S_ISDIR(s.st_mode):
                rec['type']="DIR"          
                # should we go deeper?        
                
                if not args['maxdepth'] or int(args['maxdepth'])>depth:                
                    for basename in os.listdir(path):
                        fullname = os.path.join(path,basename)
                        subout = self.getrec(fullname,args,depth+1)
                        out.extend(subout)

            elif stat.S_ISCHR(s.st_mode):
                rec['type']="CHR"
            elif stat.S_ISBLK(s.st_mode):
                rec['type']="BLK"
            elif stat.S_ISREG(s.st_mode):
                rec['type']="REG"
                if args['md5']:
                   rec['md5'] = hashfile(open(path,'rb'), hashlib.md5())
                if args['sha1']:
                   rec['sha1'] = hashfile(open(path,'rb'), hashlib.sha1())
                if args['sha256']:
                   rec['sha256'] = hashfile(open(path,'rb'), hashlib.sha256())

                
            elif stat.S_ISFIFO(s.st_mode):
                rec['type']="FIFO"
            elif stat.S_ISLNK(s.st_mode):
                rec['type']="LNK"
            elif stat.S_ISSOCK(s.st_mode):
                rec['type']="SOCK"
                                           
            if depth>=int(args['mindepth']):
                out.append(rec)                    
        except (IOError, OSError, PermissionError, FileNotFoundError) as e:
            self.ts.oc.log.error("exception:"+str(e))
#        print("return:",path,out)
        return out

    
    def run(self,ts,data,args):
        self.ts = ts                   
        if not isinstance(data,list):
            data=[]
        
        if args['path']:
            data.extend(self.getrec(args['path'],args,0))        
        else:
            self.ts.oc.log.error('DIR requires path, e.g. DIR path=/var/log or DIR path=/var/log/mail.log')
        return data

DirProc('DIR',ts.TaskSeq)        

class DFProc(FsTaskProcessor):
    help='free disk space'
    defconf={'path': ''}

    @staticmethod
    def usage2g(u):
        g=1024*1024*1024 # 1GB

        d={}
            
        d['total']=u.total
        d['used']=u.used
        d['free']=u.free

        d['totalg']=int(u.total/g)
        d['usedg']=int(u.used/g)
        d['freeg']=int(u.free/g)

        
        d['percent']=u.percent
        return d
    
    
    def run(self,ts,data,args):
        self.ts = ts

        if args['path']:
            u = psutil.disk_usage(args['path'])            
            d = DFProc.usage2g(u)
            d['path']=args['path']
            return d
        else:
            dflist=[]            
            for p in psutil.disk_partitions():
                u = psutil.disk_usage(p.mountpoint)
                d = DFProc.usage2g(u)
                d['path']=p.mountpoint
                dflist.append(d)
            return dflist

DFProc('DF',ts.TaskSeq)        
            

