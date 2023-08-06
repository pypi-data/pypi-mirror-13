from datetime import datetime
from datetime import timedelta

def delta2dict( delta ):
    """Accepts a delta, returns a dictionary of units"""
    delta = abs( delta )
    return { 
        'year'   : int(delta.days / 365),
        'day'    : int(delta.days % 365),
        'hour'   : int(delta.seconds / 3600),
        'minute' : int(delta.seconds / 60) % 60,
        'second' : delta.seconds % 60,
        'microsecond' : delta.microseconds
    }

def human(dt, precision=2, past_tense='{} ago', future_tense='in {}', abbreviate=False):
    """Accept a datetime or timedelta, return a human readable delta string"""
    delta = dt
    if type(dt) is not type(timedelta()):
        delta = datetime.now() - dt
     
    the_tense = past_tense
    if delta < timedelta(0):
        the_tense = future_tense

    d = delta2dict( delta )

    hlist = [] 
    count = 0
    units = ( 'year', 'day', 'hour', 'minute', 'second', 'microsecond' )
    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        if abbreviate:
            abr = 'ms' if unit == 'microsecond' else unit[0]
            hlist.append('{}{}'.format(d[unit], abr))
        else:
            s = '' if d[ unit ] == 1 else 's' # handle plurals
            hlist.append('{} {}{}'.format(d[unit], unit, s))
        count += 1

    return the_tense.format(', '.join(hlist)) 
