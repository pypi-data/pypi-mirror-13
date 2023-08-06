"""Mit diesem Modul werden verschachtelte Listen auf der Standardausgabe ausgegeben"""

def print_lvl(liste, einzug=False, ebene=0):
    """Die übergebene Liste wird daraufhin geprüft, ob es sich um eine Liste handelt.
    Ist dies der Fall wird diese Funktion solange aufgerufen, bis das erste Element, dass
    keine Liste ist erreicht wurde.
    Dem Modul können die optionalen Parameter einzug und ebene mitgegeben werden. Mit einzug
    kann der Einzug aktiviert werden. Mit ebene kann bestimmt werden auf welcher Ebene der Einzug
    beginne soll."""
    for element in liste:
        if isinstance(element, list):
            print_lvl(element,einzug, ebene+1)
        else:
            if einzug == True:
                for tab in range (ebene):
                    print("\t",end='')
            print (element)

