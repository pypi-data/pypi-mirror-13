"""This is "datanester.py" module, and it provides one function called data_nest()
which prints lists that may or may not include nested lists."""

def data_nest(data_list,indent=False,level=0):
    """This function takes a positional argument called "data_list" , which is any
        Python list (of,possibly,nested lists). Each data item in the provided list
        is (recursively) printed to the screen on its own line."""
    for data in data_list:
        if isinstance(data,list):
            data_nest(data,indent,level+1)
        else:
            if indent:            
                for data_tab in range(level):
                    print("\t",end='')
            print(data)
            
lists = ["xyz","lol",["is","my",["name"]]]
