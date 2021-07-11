import re
import sys
import lxml
import requests

from bs4 import BeautifulSoup
from optparse import OptionParser

class GoogleImageSearch(object):

    def __init__(self,config_dict={}):

        self.urls = []
        GoogleImageSearch.number_of_results = config_dict['count']

    @staticmethod
    def pairs(padding=None):
        if GoogleImageSearch.number_of_results == 25:
            return [[1, 10],[11, 20],[21, 25]]
        elif GoogleImageSearch.number_of_results == 50:
            return [[1, 10],[11, 20],[21, 30],[31,40], [41,50]]
        elif GoogleImageSearch.number_of_results == 75:
            return [[1, 10],[11, 20],[21, 30],[31,40], [41,50],[51,60],[61,70],[71,75]]
        elif GoogleImageSearch.number_of_results == 100:
            return [[1, 10],[11, 20],[21, 30],[31,40],[41,50],[51,60],[61,70],[71,80],[81,90],[91,100]]
        return [[1, 10]]

    def get_links(self,query):

        query  = re.sub(' ','+',query)

        for pair in GoogleImageSearch.pairs():

            pair0 = str(pair[0])
            pair1 = str(pair[1])

            r    = requests.get("https://www.google.com/search?q="+query+"&tbm=isch&start="+pair0+"&num="+pair1)
            html = r.content
            soup = BeautifulSoup(html, 'html.parser')

            for link in soup.find_all('img'):
                src = link.get('src')
                if re.search('.gif', src, re.I) is None:
                    if not src in self.urls:
                        self.urls.append(src)
        return self.urls

    def generate_curl_commands(self,urls):
        for count in range(0,len(urls)):
            print("curl '"+urls[count]+"' --output "+str(count)+".jpg")

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-c', '--count',
        dest='count', type='int', default=10,
        help='The number of links to retrieve.')

    parser.add_option('-q', '--query',
        dest='query', default='',
        help='What we are searching for.')

    (options, args) = parser.parse_args()

    config_dict = {
        'count': options.count, 'query': options.query
    }

    google_image_search = GoogleImageSearch(config_dict)
    if not config_dict['query']:
        print('[ERROR] (GoogleImageSearch.__main__) Please provide a search query!')
        sys.exit(0)
    google_image_search.generate_curl_commands(google_image_search.get_links(config_dict['query']))
