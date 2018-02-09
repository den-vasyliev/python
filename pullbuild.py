#v.0902-1700
import commands, sys, getopt, os.path, re, time, jenkins
from fabric.api import run, env, cd, roles, hide, remote_tunnel
from fabric.state import output
from urllib import quote 
from fabric.operations import local as lrun

output['everything'] = False
output['status'] = False

def production_env(branch, artifact):
    env.core_list=['19','24','25','35']    
    env.disable_known_hosts = 'true'
    env.jenkinsHost		          = 'http://127.0.0.1:456'
    env.diskPath            = '/builds/'
    env.buildArtifact       = artifact
    env.user                = 'ubuntu'
    env.hosts               = ['localhost']
    tag 			              = 'lastSuccessfulBuild'
    env.key_filename      	= '~/.ssh/qsc-core.rsa' 
    env.nc                  = 'nc -w 1 -z 172.22.171.'
    env.curl                = 'curl -v -u admin:admin123'
    env.wget                = 'wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 3 --continue'
    env.wgetRetry           = 3
    env.tunnel              = 'ssh -i %s -f -N -L 456:10.104.31.6:8080 172.22.171.' % (env.key_filename)
    env.nexus               = 'http://localhost:8081/repository/builds'
    env.kill                = 'kill $(pgrep -f "456:")'
    env.buildUrl           	    = '/job/%s/%s/artifact/' % (branch, tag)
    env.cmdBuildNumber      = 'wget -qO- %s/job/%s/%s/buildNumber' % (env.jenkinsHost, branch, tag)
    env.cmdBuildSize        = '--spider -o -|grep Length|cut -d " " -f 2'


def pullbuild(branch, artifact):
  start = time.time()
  production_env(branch, artifact)
  sshTunnel()

  buildInfo = jbuildInfo(branch)
  buildFileSize = ckSize(buildInfo['diskFile'],buildInfo['buildUrl'])

  if buildFileSize['result']:
    print 'Already pulled: %s (%s/%s)' % (buildInfo['buildName'], buildFileSize['size'], buildFileSize['remote_size'])
    killTunnel()
    nextJob(branch)
    end = time.time()
    print 'Timer: %f' % (end - start)
    return 1

  print 'Build: ' + buildInfo['buildName']
  for x in range(0, env.wgetRetry):
    if buildFileSize['result']:
      print 'Successful: %s (%s/%s)' % (buildInfo['diskFile'], buildFileSize['size'], buildFileSize['remote_size'])
      break
    else:
      print 'Pulling a build: %s (%s/%s)' % (buildInfo['buildUrl'], buildFileSize['size'], buildFileSize['remote_size'])
      lrun( (env.wget + ' %s -O %s') % (buildInfo['buildUrl'], buildInfo['diskFile']))
      buildFileSize = ckSize(buildInfo['diskFile'],buildInfo['buildUrl'])

  killTunnel()
  nextJob(branch)
  nexusUpload(branch, buildInfo['diskFile'], buildInfo['buildName'], buildInfo['fileName'])
  
  end = time.time()
  print 'Timer: %f' % (end - start)
  return 0
 
def killTunnel():
      lrun('echo "kill $(pgrep -of 456)"|at now+1min')
      print 'Close tunnel: ' + lrun('atq|sort -r|head -1', capture=True)
      return 0
      
def nextJob(branch):
      lrun('echo "fab -f ~/pullbuild.py pullbuild:branch="' + branch + '|at tomorrow', capture=True)
      print 'Schedule next: ' + lrun('atq|sort -r| head -1', capture=True)
      return 0
      
def sshTunnel():
      for jumpHost in env.core_list:
        jumpHostAlive = lrun(env.nc + jumpHost + ' 22;echo $?', capture=True)
        if int(jumpHostAlive) == 0:
          print 'Jumphost: ' + jumpHost
          lrun(env.tunnel + jumpHost,capture=False)
          print 'Tunnel: ' + env.tunnel + jumpHost
          return 0

def nexusUpload(branch, diskFile, buildName, fileName):
      cmdNexusUpload  = '%s --upload-file %s %s/%s/%s/%s' % (env.curl, diskFile, env.nexus, branch, buildName, fileName)
      lrun(cmdNexusUpload, capture=True)
      print 'Nexus Path: %s/%s/%s' % (branch, buildName, buildName)
      return 0

def ckSize(diskFile, buildUrl):

      jbuildSize = lrun( (env.wget + ' %s %s') % (buildUrl, env.cmdBuildSize), capture=True )
      if os.path.exists(diskFile):
        diskSize = os.path.getsize(diskFile)
        if int(diskSize) == int(jbuildSize):
          return {'result': 1, 'size': diskSize, 'remote_size': jbuildSize}
        return {'result': 0, 'size': 0, 'remote_size': jbuildSize}
      return {'result': 0, 'size': 0, 'remote_size': jbuildSize}


def jbuildInfo(branch):
    jServer = jenkins.Jenkins(env.jenkinsHost, username='', password='')
    jbuildNumber = jServer.get_job_info(branch)['lastSuccessfulBuild']['number']
    jbuildInfo = jServer.get_build_info(branch, jbuildNumber)

    jbuildArtifacts = jbuildInfo['artifacts']
    
    for artifact in jbuildArtifacts:
      if artifact['fileName'].find(env.buildArtifact) > 0:

        jbuildUrl = env.jenkinsHost + quote(env.buildUrl + artifact['relativePath'])
        jbuildName = jbuildInfo['displayName'].replace(' ','')
        jfileName = artifact['fileName'].replace(' ','_')
        jdiskFile = env.diskPath + jbuildName + ':' + jfileName

        return {'buildUrl': jbuildUrl, 'buildName': jbuildName, 'diskFile': jdiskFile, 'fileName': jfileName}
  
##