"""Este módulo es nester.py y provee una función llamada print_lol que permite imprimir en pantalla una lista que dentro
de sus items contenga listas anidadas y dentro de esas listas anidadas contenga otras listas anidadas y así sucesivamente..."""

def print_lol(the_list):
        """Esta función valida que cada ítem que contiene la lista no sea una lista y si es una lista se llama a sí mismo
        para validarla siguiente lista en caso de lo contrario imprime los ítems en pantalla"""
        
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item)
                else: print(each_item)
		
