import urllib,sys,json

url = 'http://10.100.31.210/service/siesta/rest/beta/assets?repositoryId=docker'
data = urllib.urlopen( url ).read()

doc = json.loads( data )
print(data)

for a in ElementPath.findall(doc, ".//items"):
#  print ( a.find("name").text + " (" +
#        a.find("id").text + ")\n\t" +
#        a.find("resourceURI").text ) + "\n"

