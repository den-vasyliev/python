"""v.1302-0340 den@msrn.me
Simply REST API Module for Nexus Repository ManagerOSS 3.8.0-0

Set nexus_config dict to begin, e.g:
nexus_config={'host':'localhost:8081','credentials':'admin:admin123'}

Returning JSON with new line at the end

Please find more on swagger http://<nexus_hostname>/#admin/system/api

Quick Start:
Upload: nexus.raw_upload(nexus_config, 'nexus.py', 'test', 'test', 'nexus.py') # Return 201
Search: query={'q': 'test'}; nexus.search(nexus_config, query) # Return JSON
Delete: nexus.components_del(nexus_config, 'YnVpbGRzOjRiMzc4NjUzNTkxYzY3MjJlNDc5Y2JmMTVjNWZhZTQ4') # Return 204

"""
from fabric.api import env
from fabric.state import output
from urllib import quote 
from fabric.operations import local as lrun

output['everything'] = False
output['status'] = False
nexus_config={'host':'localhost:8081','credentials':'admin:admin123'}

def raw_upload(nexus_config, diskFile, branch, buildName, fileName):
  """Upload file to RAW repository
  201 Created"""
  NexusUpload  = """curl -s -o /dev/null -I -w "%s" -u %s --upload-file %s http://%s/repository/builds/%s/%s/%s""" % ('%{http_code}', nexus_config['credentials'], diskFile, nexus_config['host'], branch, buildName, fileName)
  result = lrun(NexusUpload, capture=True)
  return result

def assets_get(nexus_config, repository):
  "<REPOSITORY> from which you would like to retrieve assets"
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/assets?repository=%s'") % (nexus_config['credentials'], nexus_config['host'], repository), capture=True)
  return result

def assets_del(nexus_config, asset_id):
  """<ID> of the asset to delete
  204 Component was successfully deleted
  403 Insufficient permissions to delete component
  404 Component not found
  422 Malformed ID"""
  result = lrun(("""curl -s -o /dev/null -I -w "%s" -X DELETE -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/assets/%s'""") % ('%{http_code}', nexus_config['credentials'], nexus_config['host'], asset_id), capture=True)
  return result

def assets_getid(nexus_config, asset_id):
  "GET <ID> of the asset to get"
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://localhost:345/service/rest/beta/assets/%s'") % (nexus_config['credentials'], nexus_config['host'], asset_id), capture=True)
  return result

def components_get(nexus_config, repository):
  """<REPOSITORY>  from which you would like to retrieve components
  204 Component was successfully deleted
  403 Insufficient permissions to delete component
  404 Component not found
  422 Malformed ID"""
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/components?repository=%s'") % (nexus_config['credentials'], nexus_config['host'], repository), capture=True)
  return result

def components_del(nexus_config, component_id):
  "<ID> of the component to delete"
  result = lrun(("""curl -s -o /dev/null -I -w "%s" -X DELETE -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/components/%s'""") % ('%{http_code}', nexus_config['credentials'], nexus_config['host'], component_id), capture=True)
  return result

def components_getid(nexus_config, component_id):
  "<ID> of the component to retrieve"
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://l%s/service/rest/beta/components/%s'") % (nexus_config['credentials'], nexus_config['host'], component_id), capture=True)
  return result

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

def search(nexus_config, query):
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
nexus.search(nexus_config, query)
  """
  query_ = ''
  for k, v in sorted(query.iteritems()): 
    query_ = '%s&%s=%s' % (query_,k,v)
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/search?%s'") % (nexus_config['credentials'], nexus_config['host'], query_), capture=True)
  return result


def search_assets(nexus_config, query):
  "Query by keyword"
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/search/assets?q=%s'") % (nexus_config['credentials'], nexus_config['host'], query), capture=True)
  return result

#GET /beta/search/assets
def search_download(nexus_config, query):
  "Query by keyword"
  result = lrun(("curl -X GET -u %s --header 'Accept: application/json' 'http://%s/service/rest/beta/search/assets/download?q=%s'") % (nexus_config['credentials'], nexus_config['host'], query), capture=True)
  return result

#GET /beta/search/assets/download
#Returns a 302 Found with location header field set to download URL. Search must return a single asset to receive download URL.

def tasks():
  "Not implemented yet"
  return 'Not implemented yet'
#get
#get
#post
#post