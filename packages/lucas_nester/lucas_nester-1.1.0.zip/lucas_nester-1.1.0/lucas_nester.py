
"""Este é o módulo "lucas_nester.py", e fornece uma função chamada print_org()
que imprime listas que podem ou não incluir listas aninhadas."""

def print_org(the_list,level):
    """Esta função requer um argumento posicional chamado "the_list", que é 
        qualquer lista Python(de possíveis listas aninhadas). Cada item de dados na
        lista fornecida é(recursivamente) impresso na tela em sua própria lista.
        Um segundo argumento chamado "level" é usado para inseir tabulações
        quando uma lista aninhada é encontrada."""

    for each_item in the_list:
        if isinstance(each_item, list):
            print_org(each_item, level+1)
        else:
             for tab_stop in range(level):
                 print("\t",end=" ")
             print(each_item)

