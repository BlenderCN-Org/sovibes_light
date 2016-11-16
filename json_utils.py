import json

# TODO Rename function, add a function to add an element in a json file

def update_key_json(tab_key, json_data, value):
    key_tab = tab_key[0]
    for key in json_data.keys():
        if key == key_tab:
            tab_key.pop(0)
            if tab_key:
                return update_key_json(tab_key, json_data[key_tab], value)
            else:
                json_data[key_tab] = value
                return True
    # New key to add
    if len(tab_key) == 1:
        json_data[key_tab] = value
        return True


def update_json_file_by_key(file_path, key, value):
    json_data = {}
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        updated = update_key_json(key, json_data, value)
        if updated:
            with open(file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=2,sort_keys=True)

def update_json_file(file_path,key,value):
    json_data={}
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        json_data[key] = value
    with open(file_path,'w')  as json_file:
        json.dump(json_data,json_file,indent=2,sort_keys=True)