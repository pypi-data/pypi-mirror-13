from __future__ import print_function

import okerrclient.taskseq as ts
import sys
import pwd
import os
import subprocess
import shlex

class RunTaskProcessor(ts.TaskProcessor):
    chapter = 'External programs processor'


class TaskRun(RunTaskProcessor):
    help = 'run program'

    parse_args=False
    store_argline='prog'


    defargs = {
        'prog': '',
    }

    tpconf = {
        'user': 'nobody',
        'safebin': []
    }

    def run(self,ts,data,args):               
            
        callarg = shlex.split(args['prog'])
        
        # is this program allowed?
        if not ('*' in self.tpconf['safebin'] or callarg[0] in self.tpconf['safebin']):
            ts.oc.log.error('{} is not in safebin: {}'.format(args['prog'], str(self.tpconf['safebin'])))
            ts.stop()            
            return None

        try:
            uid = pwd.getpwnam(self.tpconf['user']).pw_uid
        except KeyError:
            ts.oc.log.error('no such user {}'.format(self.tpconf['user']))
            ts.stop()            
            return None
        
               
        p = subprocess.Popen(callarg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn = lambda: os.setuid(uid))
        p.wait()
        res = p.communicate()
        
        if p.returncode or res[1]:
            ts.oc.log.error('error code: {}, stderr: {}'.format(p.returncode, res[1]))
            ts.stop()            
            return None
    
        return res[0].split('\n')
                
TaskRun('RUN', ts.TaskSeq)

        

