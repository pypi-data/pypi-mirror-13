"""nester_435 fornece uma função chamada print_lol() que imprime os dados de
uma lista. Esta função aceita como argumentos de entrada uma lista, True or
False como opções de indentação, no caso de listas aninhadas, e level, que
deve ser um integer com a quantidade de espaço em cada indentação"""

def print_lol(the_list, indent = False, level=0, fh = sys.stdout):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='', file=fh)
            print(each_item, file=fh)
