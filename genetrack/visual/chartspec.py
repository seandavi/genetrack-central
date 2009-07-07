"""
Parses a chart specification from a text
"""
testlines = """

#
# track spec
#

row=1;   color  =  RED; glyph=BAR; data=8946;

  row =  2   ; color=BLUE; glyph  =ORF; data= 34555;      

row=2; color=GOLD; glyph=ORF; data=15664;        


"""
from genetrack import logger
from string import strip

def split(text, sep):
    return map(strip, text.split(sep))

def glyph_check(value):
    return str(value)

def color_check(value):
    return str(value)

# maps dictionarly keys to validation functions
validator = dict(
    data=int, row=int, layer=int, glyph=glyph_check, color=color_check, 
    height=int, 
    )

REQUIRED = set('row data glyph'.split())

def parse(text):
    """
    Parses a text and attempts to return a dictionary
    """
    data, errmsg = [], None

    # keep only lines with content
    lines = map(strip, text.splitlines())
    lines = filter(None, lines)
    lines = filter(lambda r: not r.startswith('#'), lines)
    
    try:
        for line in lines:
            row = {}
            data.append( row )
            line  = line.rstrip(';')
            pairs = split(line, ';')
            for pair in pairs:
                key, value = split(pair, '=')
                row[key.lower()] = validator[key](value.upper() )
    except KeyError, exc:
        errmsg = 'Unknown attribute: %s' % exc
    except ValueError, exc:
        errmsg = 'Attribute error: %s' % exc
    except Exception, exc:
        errmsg = str(exc)
    
    if not data:
        errmsg = "Field must contain at least one track. Click 'Add' above."

    for entry in data:
        diff = REQUIRED - set(entry.keys())
        if diff:
            errmsg = 'Required attributes: %s' % ', '.join(diff)

    if errmsg:
        logger.error('Track validation error %s' % errmsg)
    return data, errmsg

def test():
    data = parse(testlines)
    print data

if __name__ == '__main__':
    test()