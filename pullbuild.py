#v.1102-1200 den@msrn.me
import commands, sys, socket, getopt, os.path, re, time, jenkins
from fabric.api import run, env, cd, roles, hide, remote_tunnel
from fabric.state import output
from urllib import quote 
from fabric.operations import local as lrun

output['everything'] = False
output['status'] = False
debug = True
log = {}
envars = ''

def setenv():
  envars = ''
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('10.255.255.255', 1))
  s.close
  myIp = s.getsockname()[0]
  enVar = {'PULLBUILD_JENKINS_HOST':'10.104.31.6','PULLBUILD_JENKINS_PORT':'8080','PULLBUILD_NEXUS_HOST':myIp,'PULLBUILD_NEXUS_PORT':'8081','PULLBUILD_SSH_KEY':'qsc-core.rsa','PULLBUILD_NEXUS_USER':'admin','PULLBUILD_NEXUS_PASSWD':'admin123','PULLBUILD_SLACK_TOKEN':'SET_ME_PLEASE'}
  for var, val in (enVar.items()):
    try:
      os.environ[var]
      envars = envars + '%s=%s\n' % (var, os.environ[var])
    except:
      os.environ[var] = val
      envars = envars + '%s=%s\n' % (var, val)
  return envars


def production_env(branch, artifact, tunnel):
    setenv()
    env.core_list=['19','24','25','35']    
    env.disable_known_hosts = 'true'
    env.useTunnel           = tunnel
    env.jenkinsHost		      = os.environ["PULLBUILD_JENKINS_HOST"]
    env.jenkinsPort         = os.environ["PULLBUILD_JENKINS_PORT"]
    env.jenkinsProto        = 'http'
    env.tunnelPort          = '456'
    env.nexusHost           = os.environ["PULLBUILD_NEXUS_HOST"]
    env.nexusPort           = os.environ["PULLBUILD_NEXUS_PORT"]
    env.nexus               = 'http://%s:%s/repository/builds' % (env.nexusHost, env.nexusPort)
    env.sshKey              = os.environ["PULLBUILD_SSH_KEY"]
    env.key_filename        = '~/.ssh/%s' % (env.sshKey)
    env.nexusUser           = os.environ["PULLBUILD_NEXUS_USER"]
    env.nexusPasswd         = os.environ["PULLBUILD_NEXUS_PASSWD"]
    env.slackToken          = os.environ["PULLBUILD_SLACK_TOKEN"]
    env.slackHook           = "curl -k -X POST -H 'Content-type: application/json' https://hooks.slack.com/services/%s --data " % (env.slackToken)
    if int(tunnel):
      env.tunnel            = 'ssh -i %s -f -N -L %s:%s:%s 172.22.171.' % (env.key_filename, env.tunnelPort, env.jenkinsHost, env.jenkinsPort)
      env.jenkinsHost       = '127.0.0.1'
      env.jenkinsPort       = env.tunnelPort
    env.jenkinsURL          = '%s://%s:%s' % (env.jenkinsProto, env.jenkinsHost, env.jenkinsPort)
    env.diskPath            = '/builds/'
    env.buildArtifact       = artifact
    env.user                = 'ubuntu'
    env.hosts               = ['localhost']
    env.tag 			          = 'lastSuccessfulBuild'
    env.nc                  = 'nc -w 1 -z '
    env.nc_core             = env.nc + '172.22.171.'
    env.curl                = 'curl -v -u %s:%s' % (env.nexusUser, env.nexusPasswd)
    env.wget                = 'wget --retry-connrefused --waitretry=10 --read-timeout=20 --timeout=15 -t 3 --continue'
    env.wgetRetry           = 3
    env.kill                = 'kill $(pgrep -f "%s:")' % (env.tunnelPort )
    env.buildUrl           	= '/job/%s/%s/artifact/' % (branch, env.tag)
    env.cmdBuildNumber      = 'wget -qO- %s/job/%s/%s/buildNumber' % (env.jenkinsURL, branch, env.tag)
    env.cmdBuildSize        = '--spider -o -|grep Length|cut -d " " -f 2'
    env.cmdNexusSize        = '--spider --http-user %s --http-password %s -o -|grep Length|cut -d " " -f 2' % (env.nexusUser, env.nexusPasswd)
    

def help():
  help = """Usage: pullbuild:branch=<BRANCH>,artifact=<ARTIFACT>,tunnel=[0|1]
Example: fab -f pullbuild.py pullbuild:RC_7.0,Admin,1

Set ENV or use defaults:

%s""" % (setenv())
  print help

def pullbuild(branch, artifact, tunnel):
  start = time.time()
  production_env(branch, artifact, tunnel)
  
  sshTunnel()
  if jHostCheck():
    killTunnel()
    Notify(log)
    return -1

  buildInfo = jbuildInfo(branch)
  nexusURL = '%s/%s/%s/%s' % (env.nexus, branch, buildInfo['buildName'], buildInfo['fileName'])
  NexusCheck  = '%s %s %s' % ('wget', nexusURL, env.cmdNexusSize)
  buildNexusSize = ckNexusSize(buildInfo['diskFile'],buildInfo['buildUrl'], NexusCheck)

  if buildNexusSize['result']:
    log[time.time()] = 'Already pulled: %s (%s/%s)' % (buildInfo['buildName'], buildNexusSize['size'], buildNexusSize['remote_size'])
    killTunnel()
    nextJob(branch)
    end = time.time()
    log[time.time()] = 'Timer: %f' % (end - start)
    log[time.time()] = 'Download URL: %s' % (nexusURL)
    Notify(log)
    return 1

  log[time.time()] =  'Build: ' + buildInfo['buildName']

  buildFileSize = ckSize(buildInfo['diskFile'],buildInfo['buildUrl'])
  error = 0

  for x in range(0, env.wgetRetry):
    if buildFileSize['result']:
      try:
        log[time.time()] = 'Pulling [%i]: %s (%s/%s)' % (x, buildInfo['buildUrl'], buildFileSize['size'], buildFileSize['remote_size'])
        lrun( (env.wget + ' %s -O %s') % (buildInfo['buildUrl'], buildInfo['diskFile']))
        error = 0
        buildFileSize = ckSize(buildInfo['diskFile'],buildInfo['buildUrl'])
      except :
        buildFileSize = ckSize(buildInfo['diskFile'],buildInfo['buildUrl'])
        log[time.time()] =  'Something went wrong: %s - Trying to pull again' % (sys.exc_info()[0])
        error = 1
    else:
      log[time.time()] = 'Successful pulled: %s (%s/%s)' % (buildInfo['diskFile'], buildFileSize['size'], buildFileSize['remote_size'])
      break    
  
  killTunnel()

  if error:
    log[time.time()] =  'Tried %s times - no success' % (env.wgetRetry)
    Notify(log)
    return 1

  nexusResult = nexusUpload(branch, buildInfo['diskFile'], buildInfo['buildName'], buildInfo['fileName'], buildFileSize['size'])
  nextJob(branch)
  
  end = time.time()
  log[time.time()] = 'Download URL: %s' % (nexusURL)
  log[time.time()] =  'Timer: %f  Retries: %i  Result: %s' % (end - start, x, nexusResult)
  Notify(log)
  return 0
 
def killTunnel():
    if int(env.useTunnel):
      lrun('echo "kill $(pgrep -of 456)"|at now+1min')
      log[time.time()] =  'Tunnel down: ' + lrun('atq|sort -r|head -1', capture=True)
      return 0
    return 0
      
def nextJob(branch):
      lrun('echo "fab -f ~/pullbuild.py pullbuild:branch="' + branch + '|at tomorrow', capture=True)
      log[time.time()] =  'Schedule next: ' + lrun('atq|sort -r| head -1', capture=True)
      return 0
      
def sshTunnel():
    if int(env.useTunnel):
      for jumpHost in env.core_list:
        jumpHostAlive = lrun(env.nc_core + jumpHost + ' 22;echo $?', capture=True)
        if int(jumpHostAlive) == 0:
          log[time.time()] =  'Jumphost: ' + jumpHost
          lrun(env.tunnel + jumpHost,capture=False)
          log[time.time()] =  'Tunnel: up'
          return 0
    return 0

def jHostCheck():
      jHostAlive = lrun(env.nc + env.jenkinsHost + ' ' + env.jenkinsPort + ';echo $?', capture=True)
      if int(jHostAlive) == 0:
        log[time.time()] =  'Connect to jenkins host %s:%s' % (env.jenkinsHost, env.jenkinsPort)
        return 0
      else:
        log[time.time()] =  'Can not connect to jenkins host %s:%s' % (env.jenkinsHost, env.jenkinsPort)
        return 1

def nexusUpload(branch, diskFile, buildName, fileName, buildFileSize):
      
      for x in range(0, env.wgetRetry):

        log[time.time()] =  'Uploading to Nexus [%i]...' % (x)
        cmdNexusUpload  = '%s --upload-file %s %s/%s/%s/%s' % (env.curl, diskFile, env.nexus, branch, buildName, fileName)
        lrun(cmdNexusUpload, capture=True)
        
        cmdNexusCheck  = '%s %s/%s/%s/%s %s' % ('wget', env.nexus, branch, buildName, fileName, env.cmdNexusSize)
        nexusFileSize = lrun(cmdNexusCheck, capture=True) or 0
        log[time.time()] =  'Nexus Check: %s/%s/%s (nexus:%s / jenkins:%s)' % (branch, buildName, fileName, nexusFileSize, buildFileSize)

        if int(nexusFileSize) == int(buildFileSize):
          log[time.time()] =  'Successful'
          nexusResult = 'Successful'
          cleanup(diskFile)
          break
        else:
          nexusResult = 'Could not upload'

      return nexusResult

def ckSize(diskFile, buildUrl):

      jbuildSize = lrun( (env.wget + ' %s %s') % (buildUrl, env.cmdBuildSize), capture=True )
      
      if os.path.exists(diskFile):
        diskSize = os.path.getsize(diskFile) or 0
        if int(diskSize) == int(jbuildSize):
          return {'result': 0, 'size': diskSize, 'remote_size': jbuildSize}
        return {'result': 1, 'size': diskSize, 'remote_size': jbuildSize}
      return {'result': 1, 'size': 0, 'remote_size': jbuildSize}

def ckNexusSize(diskFile, buildUrl, NexusCheck):

      jbuildSize = lrun( (env.wget + ' %s %s') % (buildUrl, env.cmdBuildSize), capture=True )
      
      nexusFileSize = lrun(NexusCheck, capture=True) or 0
      if int(nexusFileSize)>0:
        if int(nexusFileSize) == int(jbuildSize):
          return {'result': 1, 'size': nexusFileSize, 'remote_size': jbuildSize}
        return {'result': 0, 'size': nexusFileSize, 'remote_size': jbuildSize}
      return {'result': 0, 'size': 0, 'remote_size': jbuildSize}

def jbuildInfo(branch):
    jServer = jenkins.Jenkins(env.jenkinsURL, username='', password='')
    jbuildNumber = jServer.get_job_info(branch)['lastSuccessfulBuild']['number']
    jbuildInfo = jServer.get_build_info(branch, jbuildNumber)

    jbuildArtifacts = jbuildInfo['artifacts']
    
    for artifact in jbuildArtifacts:
      if artifact['fileName'].find(env.buildArtifact) > 0:

        jbuildUrl = env.jenkinsURL + quote(env.buildUrl + artifact['relativePath'])
        jbuildName = jbuildInfo['displayName'].replace(' ','')
        jfileName = artifact['fileName'].replace(' ','_')
        jdiskFile = env.diskPath + jbuildName + ':' + jfileName

        return {'buildUrl': jbuildUrl, 'buildName': jbuildName, 'diskFile': jdiskFile, 'fileName': jfileName}

def cleanup(diskFile):
    os.remove(diskFile)
    log[time.time()] =  'Disk cleanup: %s' % (diskFile)

def Notify(log):
    message = ''
    for k, v in sorted(log.iteritems()): 
      message = message + v + '\n'
    if debug:
      print message
    env.slackHook = env.slackHook + """'{"text": "%s"}'""" % (message)
    lrun(env.slackHook, capture=False)

##