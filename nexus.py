"""v.1302-0340 den@msrn.me
Simply REST API Module for Nexus Repository ManagerOSS 3.8.0-0
https://raw.githubusercontent.com/den-vasyliev/python/master/nexus.py

Please find more on swagger http://<nexus_hostname>/#admin/system/api

Quick Start:
Credentials: nexusConfig={'host':'localhost:8081','credentials':'admin:admin123'}
Upload: nexus.rawUpload(nexusConfig, 'nexus.py', 'test', 'test', 'nexus.py') # Return 201
Search: nexus.search(nexusConfig, {'q': 'test'}) # Return JSON
Delete: nexus.componentsDel(nexusConfig, 'YnVpbGRzOjRiMzc4NjUzNTkxYzY3MjJlNDc5Y2JmMTVjNWZhZTQ4') # Return 204

"""
import subprocess

def _env(nexusConfig, type):
  curl = ["curl -s -X GET -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta" % (nexusConfig['credentials'],nexusConfig['host']), 
  """curl -s -o /dev/null -I -w "%s" -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta""" % ('%{http_code}', nexusConfig['credentials'], nexusConfig['host'])]
  return curl[type]

def _run(cmd):
  result = subprocess.check_output(['bash','-c', cmd])
  return result
  
def rawUpload(nexusConfig, diskFile, branchName, buildName, fileName):
  """Upload file to RAW repository
  201 Created"""
  cmd  = """curl -s -o /dev/null -I -w "%s" -u %s --upload-file %s http://%s/repository/builds/%s/%s/%s""" % ('%{http_code}', nexusConfig['credentials'], diskFile, nexusConfig['host'], branchName, buildName, fileName)
  return _run(cmd)

def assetsGet(nexusConfig, repository):
  "<REPOSITORY> from which you would like to retrieve assets"
  cmd = "%s/assets?repository=%s'" % (_env(nexusConfig, 0), repository)
  return _run(cmd)

def assetsDel(nexusConfig, asset_id):
  """<ID> of the asset to delete
  204 Component was successfully deleted
  403 Insufficient permissions to delete component
  404 Component not found
  422 Malformed ID"""
  cmd = """%s/assets/%s' -X DELETE """ % (_env(nexusConfig, 1), asset_id)
  return _run(cmd)

def assetsGetid(nexusConfig, asset_id):
  "GET <ID> of the asset to get"
  cmd = "%s/assets/%s'" % (_env(nexusConfig, 0), asset_id)
  return _run(cmd)

def componentsGet(nexusConfig, repository):
  """<REPOSITORY>  from which you would like to retrieve components
  204 Component was successfully deleted
  403 Insufficient permissions to delete component
  404 Component not found
  422 Malformed ID"""
  cmd = "%s/components?repository=%s'" % (_env(nexusConfig, 0), repository)
  return _run(cmd)

def componentsDel(nexusConfig, component_id):
  "<ID> of the component to delete"
  cmd = """%s/components/%s' -X DELETE """ % (_env(nexusConfig, 1), component_id)
  return _run(cmd)

def componentsGetid(nexusConfig, component_id):
  "<ID> of the component to retrieve"
  cmd = "%s/components/%s'" % (_env(nexusConfig, 0), component_id)
  return _run(cmd)

def readonly():
  "Not implemented yet"
#get
#post
#post
#post
  return 'Not implemented yet'

def script():
  "Not implemented yet"
#get
#post
#delete
#get
#put
#post
  return 'Not implemented yet'

def search(nexusConfig, query):
  """Query by param and keyword
query is a dict 'param':'keyword'
Param in:
q|repository|format|group|name|version|
md5|sha1|sha256|sha512|
docker.imageName|docker.imageTag|docker.layerId|docker.contentDigest|
maven.groupId|maven.artifactId|maven.baseVersion|maven.extension|maven.classifier|
npm.scope|nuget.id|nuget.tags|
pypi.classifiers|pypi.description|pypi.keywords|pypi.summary|
rubygems.description|rubygems.platform|rubygems.summary|yum.architecture

Example:
query={'q':'qlmm-mvp-1802', 'repository':'builds'}
nexus.search(nexusConfig, query)
  """
  query_ = ''
  for k, v in sorted(query.iteritems()): 
    query_ = '%s&%s=%s' % (query_,k,v)
  cmd = "%s/search?%s'" % (_env(nexusConfig, 0), query_)
  return _run(cmd)


def searchAssets(nexusConfig, query):
  "Query by keyword"
  cmd = "%s/search/assets?q=%s'" % (_env(nexusConfig, 0), query)
  return _run(cmd)

#GET /beta/search/assets
def searchDownload(nexusConfig, query):
  "Query by keyword"
  cmd = "%s/search/assets/download?q=%s'" % (_env(nexusConfig, 0), query)
  return _run(cmd)

#GET /beta/search/assets/download
#Returns a 302 Found with location header field set to download URL. Search must return a single asset to receive download URL.

def tasks():
  "Not implemented yet"
  return 'Not implemented yet'
#get
#get
#post
#post