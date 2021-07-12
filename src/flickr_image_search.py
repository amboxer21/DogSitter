import re
import sys
import shutil
import requests
import flickrapi

from optparse import OptionParser

class Credentials(object):

    @staticmethod
    def flickr(CREDENTIALS={}):
        with open('/etc/flickr.conf') as f:
            for line in [lines for lines in f.readlines()]:

                key    = re.search('(KEY:)([\w\d]+)',str(line))
                secret = re.search('(SECRET:)([\w\d]+)',str(line)) 

                if key is not None:
                    CREDENTIALS['KEY'] = str(key.group(2))

                if secret is not None:
                    CREDENTIALS['SECRET'] = str(secret.group(2))

        return CREDENTIALS

class FlickrImageSearch(object):

    def __init__(self,config_dict={}):

        self.key      = config_dict['key']
        self.query    = config_dict['query']
        self.secret   = config_dict['secret']
        self.count    = int(config_dict['count'])
        self.generate = bool(config_dict['generate'])
        self.download = bool(config_dict['download'])

    def flickr_photos(self):

        flickr  = flickrapi.FlickrAPI(self.key, self.secret, format='parsed-json')
        extras  = 'url_m,url_l,url_t,url_n,url_o,url_sq,url_s,url_q,url_z,url_c'
        types   = [i for i in extras.split(",")]
        results = flickr.photos.search(text=self.query, per_page=self.count, extras=extras)

        for url in results['photos']['photo']:
            if self.generate and self.download:
                print('{ERROR] (FlickrImageSearch.flickr_photos) - Generating url links and downloading images are mutally exclusive features.')
                sys.exit(0)
            elif self.download:
                for u_type in types:
                    try:
                        self.download_image(url['url_m'])
                        break
                    except KeyError:
                        pass
            elif self.generate:
                for u_type in types:
                    try:
                        print(url[u_type])
                        break
                    except KeyError:
                        pass

    def download_image(self,url):

        fname = url.split("/")[-1]
        req   = requests.get(url, stream = True)

        # Check if the image was retrieved successfully
        if req.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            req.raw.decode_content = True
    
            # Open a local file with wb ( write binary ) permission.
            with open(fname,'wb') as f:
                shutil.copyfileobj(req.raw, f)
        
            print('Image('+url+') sucessfully Downloaded.')
        else:
            print('Image('+url+') Couldn\'t be retreived.')

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-c', '--count',
        dest='count', type='int', default=10,
        help='The number of links to retrieve.')

    parser.add_option('-q', '--query',
        dest='query', default='',
        help='What we are searching for.')

    parser.add_option('-d', '--download',
        dest='download', action='store_true', default=False,
        help='Save images to disk?')

    parser.add_option('-g', '--generate',
        dest='generate', action='store_true', default=False,
        help='Generate urls and print them to screen.')

    parser.add_option('-k', '--key',
        dest='key', default='',
        help='Flickr key.')

    parser.add_option('-s', '--secret',
        dest='secret', default='',
        help='Flickr secret.')

    (options, args) = parser.parse_args()

    credentials = Credentials.flickr()

    if not options.key:
        try:
            options.key = credentials['KEY']
        except KeyError:
            options.key = None
    
    if not options.secret:
        try:
            options.secret = credentials['SECRET'] 
        except KeyError:
            options.secret = None

    if options.key is None and options.secret is None:
        print('[ERROR] Both Flickr key and Flickr secret are required to use this program.')
        sys.exit(0)
        
    config_dict = {
        'key': options.key,
        'count': options.count,
        'query': options.query,
        'secret': options.secret,
        'download': options.download,
        'generate': options.generate,
    }

    flickr_image_search = FlickrImageSearch(config_dict)
    flickr_image_search.flickr_photos()
