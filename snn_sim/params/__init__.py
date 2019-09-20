import json

default_fn = "params/default_params.json"
user_fn = "params/user_params.json"

###########################################################
#                                                         #
# Setup step involves copying default params to user      #
# params file and changing user-defined params            #
#                                                         #
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
#                                                         #
# Get requested parameter values from the json file       #
#                                                         #
###########################################################
def get(*pars):
    data = {}

    # Read user-defined parameters into a dict
    with open(user_fn) as f:
        data = json.load(f)

    # Return the requested parameter values
    # List comprehension only works for more than one arg
    if len(pars) == 1:
        return data[pars[0]]
    else:
        return [data[par] for par in pars]
