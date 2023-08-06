"""Mit diesem Modul werden verschachtelte Listen auf der Standardausgabe ausgegeben"""

def print_lvl(liste, ebene=0):
    """Die übergebene Liste wird daraufhin geprüft, ob es sich um eine Liste handelt.
    Ist dies der Fall wird diese Funktion solange aufgerufen, bis das erste Element, dass
    keine Liste ist erreicht wurde"""
    for element in liste:
        if isinstance(element, list):
            print_lvl(element,ebene+1)
        else:
            for tab in range (ebene):
                print("\t",end='')
            print (element)

