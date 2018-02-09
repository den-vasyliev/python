import commands, sys, getopt, os.path, re
from ifparser import Ifcfg
from fabric.api import run, env, cd, roles, hide
from fabric.state import output

output['everything'] = False
output['status'] = False
#env.roledefs['monitoring'] = ['172.22.171.24']#,'172.22.171.19','172.22.171.35','172.22.171.25']

def production_env(interface, pgrep, pstat):

    env.key_filename  = '/opt/cacti/.ssh/ssh' 
    env.user          = 'root'  
    env.shell         = '/usr/bin/bash -c'
    env.int_command   = 'ifconfig %s 2>&1' % (interface)
    env.proc_command  = 'tr -d %s:kB[[:space:]] < <(grep %s /proc/$(pgrep -of [^]]%s)/status)' % (pstat, pstat, pgrep)
    env.proc_count    = 'pgrep -f [^]]%s' % (pgrep)
    env.top_command   = 'top -b -n1'
    env.monitor_count = 'sed -n "/\[%s\].*%s/p" %s*|sed -n "$=";sed -i "s/\[\(%s\]\)\(.*\)\(%s\)/\[checked-\\1\\2\\3/" %s*' % (pgrep, pstat, interface, pgrep, pstat, interface)

#@roles('monitoring')
def interface_stat(interface):
  production_env(interface,0,0)
  ifdata = Ifcfg(''.join(list(filter(lambda x:'getcwd' not in x, run(env.int_command,quiet=True,stderr='/tmp/result').rsplit('\n')))))
  int_stat = ifdata.get_interface(interface)
  print 'rxbits:%s txbits:%s rxpkts:%s txpkts:%s rxdroppedpkts:%s txdroppedpkts:%s rxerrors:%s txerrors:%s' % (int_stat.rxbytes,int_stat.txbytes,int_stat.rxpkts,int_stat.txpkts,int_stat.rxdroppedpkts,int_stat.txdroppedpkts or 0,int_stat.rxerrors,int_stat.txerrors or 0)

#@roles('monitoring')  
def proc_stat(pgrep,pstat):
  production_env(0,pgrep,pstat)
  print pstat+':'+''.join(re.findall(r'\d+', run(env.proc_command,quiet=True,stderr='/dev/null')))+' PCount:'+str(len(re.findall(r'\d+', run(env.proc_count,quiet=True,stderr='/dev/null'))))

#@roles('monitoring')
def top_stat(pgrep):
  production_env(0,pgrep,0)
  pid=str(re.findall(r'\d+',''.join(run('pgrep -of '+pgrep,quiet=True,stderr='/tmp/result')))[0])
  result = list(filter(lambda x:pid in x, run(env.top_command,quiet=True,stderr='/dev/null').rsplit('\n')))
  result = re.findall(r'\d+',result[0])
  print 'cpu:%s mem:%s' % (result[5],result[3])

def monitor_count(interface, pgrep, pstat):
  production_env(interface, pgrep, pstat)
  result = str(''.join(list(filter(lambda x:'getcwd' not in x, run(env.monitor_count,quiet=True,stderr='/dev/null')))))
  result = re.findall(r'\d+',result)
  print '%s:%s' % (pstat, result[0] if 0 < len(result) else 0)
