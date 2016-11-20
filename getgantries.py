import json
import urllib
from urlparse import urlparse
import httplib2 as http #External library

if __name__=="__main__":
    #Authentication parameters
    headers = { 'AccountKey' : 'e8QwDxUKil/yStAu0SDRlQ==', 'accept' : 'application/json'} # this is by default

    #API parameters
    uri = 'http://datamall2.mytransport.sg/' #Resource URL
    path = '/ltaodataservice/ERPRates?$skip={}'

    #Build query string & specify type of API call
    requesting = True
    total_data = []
    skip = 0

    while requesting:
        target = urlparse(uri + path.format(skip)) 
        print target.geturl()
        method = 'GET'
        body = ''

        #Get handle to http
        h = http.Http()
        #Obtain results
        response, content = h.request(
            target.geturl(),
            method,
            body,
            headers)
        #Parse JSON to print
        print('content', content)
        jsonObj = json.loads(content)
        if len(jsonObj['value']) > 0:
            total_data = total_data + jsonObj['value']
            print 'jsonobj', json.dumps(jsonObj, sort_keys=True, indent=4)
            skip += 50
        else:
            requesting = False
    
    with open("erprates.json","w") as outfile:
        json.dump(total_data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
