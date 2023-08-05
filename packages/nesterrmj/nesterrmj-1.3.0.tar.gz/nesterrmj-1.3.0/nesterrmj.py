
"""Este é o módulo "nesterrmj.py", e fornece uma função chamada print_lol()
que imprime listas que podem ou não incluir listas aninhadas."""



def print_lol(the_list, ident=False, level=0):
    """
    usage print_lol(list, ident, level) where list a python list,
    "ident" can be: 0 (identation OFF) or 1 (identation ON)
    "level" is a int number where identation tabs might start.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, ident, level+1)
        else:
            if ident:
                for tab_stop in range(level):
                    print("\t", end='')
            print(each_item)

    
