"""v.1402-1550 denys.vasyliev@qsc.com
Simply REST API Module for Nexus Repository ManagerOSS 3.8.0-0
https://raw.githubusercontent.com/den-vasyliev/python/master/nexus.py

Please find more on swagger http://<nexus_hostname>/#admin/system/api

Quick Start:
Credentials: nexusConfig={'host':'localhost:8081','credentials':['admin','admin123']}
Upload: nexus.rawUpload(nexusConfig, 'builds','nexus.py', 'test', 'test', 'nexus.py') # Return 201
Search: nexus.search(nexusConfig, {'q': 'test'}) # Return JSON
Delete: nexus.componentsDel(nexusConfig, 'YnVpbGRzOjRiMzc4NjUzNTkxYzY3MjJlNDc5Y2JmMTVjNWZhZTQ4') # Return 204

"""
import subprocess, requests

nexusConfig={'host':'localhost:8081','credentials':['admin','admin123']}

def _run(cmd, opt='get'):
  auth = (nexusConfig['credentials'])
  headers = {'Accept': 'application/json'}
  url = 'http://%s/service/rest/beta/%s' % (nexusConfig['host'], cmd)

  if opt == 'get':
    result = requests.get(url, headers=headers, auth=(nexusConfig['credentials'][0],nexusConfig['credentials'][1]))
  elif opt == 'delete':
    result = requests.delete(url, headers=headers, auth=(nexusConfig['credentials'][0],nexusConfig['credentials'][1]))
  else:
    url = 'http://%s/repository/%s' % (nexusConfig['host'], cmd)
    files = {'file': open(opt, 'rb')}
    result = requests.put(url, files=files, auth=(nexusConfig['credentials'][0],nexusConfig['credentials'][1]))
    
  return result.status_code, result.text
  
def upload(repo, branchName, buildName, fileName):
  """Upload file to RAW repository
  201 Created"""
  cmd  = "%s/%s/%s/%s" % (repo, branchName, buildName, fileName)
  return _run(cmd, fileName)

def assetsGet(repository):
  "<REPOSITORY> from which you would like to retrieve assets"
  cmd = "assets?repository=%s" % (repository)
  return _run(cmd)

def assetsDel(asset_id):
  """<ID> of the asset to delete
  204 Component was successfully deleted
  403 Insufficient permissions to delete component
  404 Component not found
  422 Malformed ID"""
  cmd = "assets/%s" % (asset_id)
  return _run(cmd,'delete')

def assetsGetId(asset_id):
  "GET <ID> of the asset to get"
  cmd = "assets/%s" % (asset_id)
  return _run(cmd)

def componentsGet(repository):
  """<REPOSITORY>  from which you would like to retrieve components
  204 Component was successfully deleted
  403 Insufficient permissions to delete component
  404 Component not found
  422 Malformed ID"""
  cmd = "components?repository=%s" % (repository)
  return _run(cmd)

def componentsDel(component_id):
  "<ID> of the component to delete"
  cmd = "components/%s" % (component_id)
  return _run(cmd, 'delete')

def componentsGetId(component_id):
  "<ID> of the component to retrieve"
  cmd = "components/%s" % (component_id)
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

def search(query):
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
  cmd = "search?%s" % (query_)
  return _run(cmd)


def searchAssets(query):
  "Query by keyword"
  cmd = "search/assets?q=%s" % (query)
  return _run(cmd)

#GET /beta/search/assets
def searchDownload(query):
  "Query by keyword"
  cmd = "search/assets/download?q=%s" % (query)
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