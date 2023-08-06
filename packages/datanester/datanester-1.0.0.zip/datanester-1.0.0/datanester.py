"""This is "datanester.py" module, and it provides one function called data_nest()
which prints lists that may or may not include nested lists."""

def data_nest(data_list):
    """This function takes a positional argument called "data_list" , which is any
        Python list (of,possibly,nested lists). Each data item in the provided list
        is (recursively) printed to the screen on its own line."""
    for data in data_list:
        if isinstance(data,list):
            data_nest(data)
        else:
            print(data)
            
