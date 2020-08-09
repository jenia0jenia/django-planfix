from collections import OrderedDict

def print_parser(obj, tab=0):
    for key, val in obj.items():
        if isinstance(val, OrderedDict):
            print(' ' * tab, key, ' : ')
            parser(val, tab + 4)
        elif isinstance(val, list):
            print(' ' * tab, key, ' : ')
            for v in val:
                if isinstance(v, OrderedDict):
                    parser(v, tab + 4)
                else:
                    print(' ' * tab, v)
        else:
            print(' ' * tab, key, ' : ', val)
