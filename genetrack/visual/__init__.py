"""
Chart and graph related modules.

"""

def test( verbose=0 ):
    """
    Initializes databases with default users and data
    then performs the doctests listed in a text file
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    "Main"
    test()