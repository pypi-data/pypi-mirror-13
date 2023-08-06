'''
This is the modul "denester.py". It provides a function called printnl()
to print a nested list which can contain any amount of embedded lists.
'''
def printnl(a_list):
    '''
    this function has one argument named "a_list", which takes any python
    list (with optionally embedded lists). The elements of the list will
    be printed out recursive. Each element will be printed out one per line.
    '''
    for element in a_list:
        if isinstance(element, list):
            printnl(element)
        else:
            print(element)
