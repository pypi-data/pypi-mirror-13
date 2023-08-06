'''
This is the modul "denester.py". It provides a function called printnl()
to print a nested list which can contain any amount of embedded lists.
'''
def printnl(a_list, indented=False, level=0):
    '''
    this function has a first argument named "a_list", which takes any python
    list (with optionally embedded lists). The elements of the list will
    be printed out recursive. Each element will be printed out one per line.
    The second argument "indented" is a boolean and specifies if the elements
    of the embedded lists will be indented according to their level ("True")
    or if it will default to no indention ("False"). The last argument "level"
    specifies the number of tabs for indention of the printed elements and
    defaults to 0.
    '''
    for element in a_list:
        if isinstance(element, list):
            printnl(element, indented, level+1)
        else:
            if indented:
                print('\t' * level, end='')
            print(element)
