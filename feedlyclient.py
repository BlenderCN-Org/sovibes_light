import json
from datetime import datetime, time
from urllib.request import urlopen

ApiUrl = "http://cloud.feedly.com"
Mixes = "/v3/mixes/contents?"
FeedMetadata = "/v3/search/feeds?"
Streams ="/v3/streams/contents?"
Search ="/v3/search/feeds?"

# Request to get a mix of the best article for a stream, return a JSON data stream
def getMix(streamId,count,hours,backfill,locale):
    Mixesrequest = ApiUrl + Mixes + 'streamId='+ streamId + '&' + 'count='+ count + '&' + 'hours='+ hours + '&' + 'backfill=' + backfill + '&' + 'locale='+locale
    #Call Mixes request
    MixResponse = urlopen(Mixesrequest)
    content = MixResponse.read()
    MixResponseText = content.decode('utf8')
    MixesJsonData = json.loads(MixResponseText)
    return MixesJsonData

def getStream(streamId, count, newerThan, continuation, ranked='newest', unreadOnly='0'):
    StreamRequest = ApiUrl + Streams + 'streamId=' + streamId + '&' + 'count='+ count + '&' + 'ranked=' + ranked + '&' + 'unreadOnly=' + unreadOnly + '&' + 'newerThan=' + newerThan +  '&' + 'continuation=' + continuation
    StreamResponse =  urlopen(StreamRequest)
    content = StreamResponse.read()
    StreamResponseText = content.decode('utf8')
    StreamJsonData = json.loads(StreamResponseText)
    return StreamJsonData

def searchFeeds(query,  locale, count=20):
    SearchRequest = ApiUrl + Search + 'query=' + query +  '&' + 'count=' + count +  '&' + 'locale=' + locale
    SearchResponse = urlopen(SearchRequest)
    content = SearchResponse.read()
    SearchResponseText = content.decode('utf8')
    SearchJsonData = json.loads(SearchResponseText)
    return SearchJsonData
    # return json.dumps(SearchJsonData, sort_keys=True, indent=2)


def getStreamIds(jsonDataText):
    streamIds = []
    jsonData = json.loads(jsonDataText)
    if jsonData.get('results'):
        for feed in jsonData['results']:
            if feed.get('feedId'):
                streamIds.append(feed['feedId'])
    return streamIds