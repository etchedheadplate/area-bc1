'''
Function allows to view nested dictionaries in human-readable form
'''

def print_json(json, indent=0): 
    for key, value in json.items():
        if isinstance(value, dict): # if value is nested dictionary
            print(' ' * indent + f'{key}:') # prints key associated with value as nested dictionary
            print_json(value, indent + 4) # recursively calls print_json() until no nested dictionaries left
        else:
            print(' ' * indent + f'{key}: {value}') # prints key and value