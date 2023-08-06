# -*- coding: utf-8 -*-
import os
import time

import cf_units
import iris

iris.FUTURE.netcdf_no_unlimited = True

def stash_id_to_name(stash_id, path_to_stash=None, default_name='unknown'):
    """ Retrieve a name from the STASH table """
    try:
        import pandas as pd 
    except ImportError:
        print('Unable to import pandas, default name returned instead')
        return default_name

    url = 'http://reference.metoffice.gov.uk/um/stash?_format=csv&_view=with_metadata'
    if path_to_stash is None:
        path_to_stash = os.path.join(os.curdir,'stash.csv')
        try:
            df = pd.read_csv(path_to_stash)
        except:
            print('File stash.csv not found')
            print('Trying to download it ...')
            try:
                import urllib
                f = urllib.request.URLopener()
                f.retrieve(url, path_to_stash)
            except:
                print('Download failed')
                print('Default name returned instead')

                return default_name

    df = pd.read_csv(path_to_stash)

    stash_label = df['rdfs:label'][df['@notation']==stash_id]
    if len(stash_label) > 0:
        return stash_label.values[0]
    else:
        print('Match not found, default name returned instead')
        return default_name


def convert_unit_str(str1, str2):
    return cf_units.Unit(str1).convert(1, cf_units.Unit(str2))


# tic toc functions ala Matlab
# Source: https://gist.github.com/tylerhartley/5174230
def tic(tag=None):
    '''Start timer function.
    tag = used to link a tic to a later toc. Can be any dictionary-able key.
    '''
    global TIC_TIME
    if tag is None:
        tag = 'default'

    try:
        TIC_TIME[tag] = time.time()
    except NameError:
        TIC_TIME = {tag: time.time()}
            
                        
def toc(tag=None, save=False, fmt=False):
    '''Timer ending function. 
    tag - used to link a toc to a previous tic. Allows multipler timers, nesting timers. 
    save - if True, returns float time to out (in seconds)
    fmt - if True, formats time in H:M:S, if False just seconds.
    '''
    global TOC_TIME
    template = 'Elapsed time is:'
    if tag is None:
        tag = 'default'
    else: 
        template = '%s - '%tag + template
        
    try:
        TOC_TIME[tag] = time.time()
    except NameError:
        TOC_TIME = {tag: time.time()}
    
    if TIC_TIME:
        d = (TOC_TIME[tag]-TIC_TIME[tag])
            
        if fmt:
            print(template + ' %s'%time.strftime('%H:%M:%S', time.gmtime(d)))
        else: 
            print(template + ' %f seconds'%(d))
        
        if save: return d
        
    else:
        print("no tic() start time available. Check global var settings")
