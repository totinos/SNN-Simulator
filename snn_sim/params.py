import json

default_fn = "default_params.json"
user_fn = "user_params.json"

###########################################################
# Setup step involves copying default params to user      #
# params file and changing user-defined params            #
###########################################################
def setup(user_params={}):
    data = {}

    # Read default parameters into dict 
    with open(default_fn) as f:
        data = json.load(f)

    # Modify the dict for each user-defined parameter
    for key, val in user_params.items():
        data[key] = val

    # Write the user parameters to a file
    with open(user_fn, "w") as f:
        jstr = json.dumps(data, indent=4)
        f.write(jstr)

    return
    
###########################################################
# Get a parameter value from the json file                #
###########################################################
def get(par):
    data = {}

    # Read user-defined parameters into a dict
    with open(user_fn) as f:
        data = json.load(f)

    # Return the requested parameter value
    return data[par]

