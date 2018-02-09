import urllib,sys
from xml.etree import ElementTree
from xml.etree import ElementPath

url = 'http://35.205.46.168:30561/nexus/service/local/data_index?q='
data = urllib.urlopen( url + sys.argv[1] ).read()

doc = ElementTree.XML( data )

for a in ElementPath.findall(doc, ".//artifact"):
  print ( a.find("groupId").text + ":" +
        a.find("artifactId").text + ":" +
        a.find("version").text )
