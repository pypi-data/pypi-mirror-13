"""

    catfish:
    transforme http://www.insee.fr/fr/service/entreprises/categorie-form.asp
    en API

    Usage:
        catfish get <siren>
        catfish batch <in_xlsx> <out_xlsx>
        catfish -h | --help
        catfish -v | --version

    options:
        -h --help       shows this screen
        -v --version    shows version

"""

import sys
import requests
from bs4 import BeautifulSoup
from docopt import docopt

# entry point url
api = 'http://www.insee.fr/fr/service/entreprises/categorie-form.asp?siren={}'

def addinterval(instr, add, interval):
    '''
        adds string every n character. returns string
    '''
    if not isinstance(instr, str):
        instr = str(instr)

    return add.join(
        instr[i:i+interval]
        for i in xrange(0,len(instr),interval))

def get(siren):
    '''
        renvoie un tuple (str, str, str, rs)
            un siren
            une categorie d'entreprise
            une annee
            une raison sociale
        param: un siren (str)

        :Example:

        >>> get('444465736')
        (u'2013', u'444465736', u'entreprise de taille interm\xe9diaire', u'NOVACAP')
        >>> get('this intended to fail')

    '''

    # format siren
    siren = addinterval(siren, ' ', 3)
    # send request
    res = requests.get(api.format(siren))

    try:
        # if request is ok
        assert res.status_code == 200
        # check if ok
        soup = BeautifulSoup(res.text, 'html.parser')
        colcentre = soup.find_all('div', id='col-centre')[0]
        l1, l2, l3 = colcentre.find_all('p')[1:4]

        if 'existe plus' in l1.text:
            return parse_obsolete(l1, l3)

        elif 'existe pas' in l1.text:
            return parse_invalid()

        elif 'hors champ' in l2.text:
            return parse_nocat()
        
        elif 'pas pu attribuer' in l1.text:
            return parse_new(l1, l2, l3)
        
        else:
            return parse_ok(l1, l3)

    except AssertionError:
        print 'site inaccessible !'

def parse_ok(l1, l3):
    '''
        parse html when siren is ok
    '''
    return {
        'annee': l1.text.split(' : ')[1].split()[2],
        'siren valide': ''.join(
            l1.text.split(' : ')[1].split(u'\xab')[0].split()[-4:-1]),
        'categorie': ' '.join(
            l1.text.split(' : ')[1].split(u'\xab')[1].split()[:-1]),
        'raison sociale': l3.text.split(' : ')[1][:-1],
        'statut': 'ok'}

def parse_obsolete(l1, l3):
    '''
        parse html when siren is obsolete
    '''
    return {
        'annee': l1.text.split('.')[2].split()[2],
        'siren valide': ''.join(
            l1.text.split('.')[2].split(u'\xab')[0].split()[-4:-1]),
        'categorie': ' '.join(
            l1.text.split('.')[2].split(u'\xab')[1].split()[:-1]),
        'raison sociale': l3.text.split(' : ')[1][:-1],
        'statut': 'obsolete'}

def parse_new(l1, l2, l3):
    '''
        parse html when siren is obsolete
    '''
    return {
        'annee': l1.text.split(' : ')[1].split()[2],
        'siren valide': ''.join(l2.text.split(' : ')[1].split()),
        'categorie': u'nouvellement cr\xe9\xe9e',
        'raison sociale': l3.text.split(' : ')[1][:-1],
        'statut': u'nouvellement cr\xe9\xe9e'}

def parse_nocat():
    '''
        parse html when siren is out of categories
    '''
    return {
        'annee': None,
        'siren valide': None,
        'categorie': 'hors champ',
        'raison sociale': None,
        'statut': 'hors champ'}

def parse_invalid():
    '''
        parse html when siren is invalid
    '''
    return {
        'annee': None,
        'siren valide': None,
        'categorie': None,
        'raison sociale': None,
        'statut': 'invalid'}

def batch(in_xlsx, out_xlsx):
    '''
        retrieves siren list from input xlsx and batches get() to output xlsx
    '''
    import pandas as pd
    import time
    import openpyxl
    pd.core.format.header_style = None

    # load file
    sirens_df = pd.read_excel(in_xlsx)

    # extract and batch sirens
    sirens_sr = sirens_df[sirens_df.columns[0]]
    sirens = [get(siren) for siren in sirens_sr]
    sirens = [str(siren).zfill(9) for siren in sirens] # <-- repair leading zeros

    # convert to dataframe and merge with initial sirens
    res = pd.DataFrame(sirens)
    final = pd.concat([sirens_df, res], axis=1)

    # save to xlsx
    tmstmp = time.strftime('%Y%m%d')
    final.to_excel(out_xlsx, sheet_name='{} results'.format(tmstmp))
    
    return 'export ok'
    

if __name__ == '__main__':
    
    args = docopt(__doc__, version='2.0')

    if args['get']:
        print get(args['<siren>'])

    if args['batch']:
        batch(args['<in_xlsx>'], args['<out_xlsx>'])
        print 'job done'
