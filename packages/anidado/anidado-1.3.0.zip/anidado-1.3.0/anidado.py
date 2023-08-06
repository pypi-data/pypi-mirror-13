"""Este módulo es nester.py y provee una función llamada print_lol que permite imprimir en
pantalla una lista que dentro de sus items contenga listas anidadas y dentro de esas listas
anidadas contenga otras listas anidadas y así sucesivamente..."""

def print_lol(the_list,level=-1):
        """Esta función valida que cada ítem que contiene la lista no sea una lista y si es
        una lista se llama a sí mismo para validar la siguiente lista en caso de lo
        contrario imprime los ítems en pantalla, un segundo argunmento es opcional para dar
        un espacio (tabulador) o varios a cada lista dependiedo de su nivel de anidación"""
        
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,level+1)
                else:
                        for num in range(level):
                                print("\t",end="")
                        print(each_item)
		
