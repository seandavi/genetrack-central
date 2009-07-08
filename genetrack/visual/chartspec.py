"""
Parses a chart specification from a text
"""
import pyparsing

test_input = """

#
# track spec
#

color  =  RED; glyph=BAR; data=8946; newrow=no;

color=BLUE; glyph  =ORF; data= 34555; row=above

;color=GOLD; glyph=ORF; data=15664;        


"""
#from genetrack import logger
from string import strip

def split(text, sep):
    return map(strip, text.split(sep))

def glyph_check(value):
    return str(value)

def color_check(value):
    return str(value)

# maps dictionarly keys to validation functions
validator = dict(
    data=int, layer=int, glyph=glyph_check, color=color_check, 
    height=int, newrow=str,
    )

REQUIRED = set('data glyph'.split())

def parse(text):
    """
    Parses a text and build a list of dictionaries based on a grammar.
    """
    
    lines = clean(text)
    
    from pyparsing import Word, Optional, OneOrMore, alphas, nums, Group
    
    alphanums = alphas + nums
    
    name  = Word(alphanums).setResultsName("name")
    value = Optional(" ") + Word(alphanums + " ").setResultsName("value")
    pair  = name + "=" + value + ";"

    expr  = OneOrMore(Group(pair))

    data, errmsg = [], None
    try:
        for line in lines:
            row = dict()
            for result in expr.parseString(line):    
                name = result.name.lower()
                value = result.value.upper()
                row[name] = validator[name](value)
            data.append(row)
    
    # trying to produce useful error messages 
    except KeyError, exc:
        errmsg = 'Unknown attribute: %s' % exc
    except ValueError, exc:
        errmsg = 'Attribute validation error: %s' % exc
    except Exception, exc:
        errmsg = str(exc)
    
    if errmsg:
        logger.error('Track validation error %s' % errmsg)
    else:
        if not data:
            errmsg = "Field must contain at least one track. Click 'Add' above."
        for entry in data:
            diff = REQUIRED - set(entry.keys())
            if diff:
                errmsg = 'Required attributes: %s' % ', '.join(diff)
    return data, errmsg

def clean(text):
    "Cleans input to contain only nonempty lines"
    lines = map(strip, text.splitlines())
    lines = filter(None, lines)
    lines = filter(lambda r: not r.startswith('#'), lines)
    lines = map(lambda x: x.strip(';'), lines)
    return lines

def test():
    data = parse(test_input)
    print data

if __name__ == '__main__':
    test()