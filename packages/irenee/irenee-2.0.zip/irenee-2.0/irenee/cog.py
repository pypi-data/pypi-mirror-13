"""
    cog:
    transforme http://www.insee.fr/fr/methodes/nomenclatures/cog/recherche_historique.asp en API
    Usage:
        cog get <start> <end> [options]
        cog (-h | --help | --version)

    Options:
        -d STR, --deplist=STR       coma separated depcodes ie 01,02...
        -m STR, --modlist=STR       coma separated modcodes ie MA,MB...
        -o FILE, --outxlsx=FILE     fully qualified path to output xlsx
"""

import sys
import urlparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from docopt import docopt

# entry point url
api = 'http://www.insee.fr/fr/methodes/nomenclatures/cog/recherche_historique.asp'

def pg2df(res):
    '''
        takes a cog requests result
        returns a table as df
    '''
    # parse res
    soup = BeautifulSoup(res.text)
    
    if u'Pas de r\xe9ponse pour cette recherche.' in soup.text:
        pass # <-- don't pass !
    
    else:
        params = urlparse.parse_qs(urlparse.urlsplit(res.url)[-2])
        tb = soup.find_all('table')[0]
        data = [
            [col.text for col in row.find_all('td')] + [params['dep'][0], params['mod'][0]]
            for row in tb.find_all('tr')[1:]] # <-- escape header row
        data = [dict(zip(
            [u'depcom', u'date', u'obs', u'dep', u'mod'], lst)) for lst in data]
            
        return pd.DataFrame(data)
    
def get(start, end, deplist=['00'], modlist=['M0'], xlsx=None):
    '''
        batch gets changelogs for cogs
    '''
    # build payloads
    if modlist == ['M0']:
        modlist = ['MA', 'MB', 'MC', 'MD', 'ME', 'MF', 'MG']
    payloads = [{'debut':start, 'fin':end, 'dep':dep, 'mod':mod} for dep in deplist for mod in modlist]
    # send requests
    results = [pg2df(requests.get(api, params=payload)) for payload in payloads]
    # make a df and fine tune it (force dtypes)
    data = pd.concat(results)
    data.reset_index()
    data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
    data[['dep', 'depcom', 'mod', 'obs']] = data[['dep', 'depcom', 'mod', 'obs']].astype(object)
    # write xlsx
    if xlsx:
        pd.core.format.header_style = None
        data.to_excel(xlsx, index=False)
    
    return pd.concat(results)

if __name__ == '__main__':
    
    args = docopt(__doc__, version='2.0')
    
    # positional agruments
    start = args['<start>']
    end = args['<end>']

    # optional agruments
    deplist = args['--deplist'].split(',') if args['--deplist'] else ['00']
    modlist = args['--modlist'].split(',') if args['--modlist'] else ['M0']
    outxlsx = args['--outxlsx'] if args['--outxlsx'] else None
    
    # go for the command line
    print get(start, end, deplist, modlist, outxlsx)
