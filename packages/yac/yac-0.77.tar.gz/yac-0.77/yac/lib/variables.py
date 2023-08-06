# yac variables are stored as:
# 
#{
#    "variable-name": {
#        "comment": "variable explanation",
#        "value":   "variable value"
#    }   
#}

def get_variable(params, variable_name, default_value=""):

    if variable_name in params and 'value' in params[variable_name]:
        return params[variable_name]['value']
    else:
        return default_value

def set_variable(params, variable_name, value, comment=""):

    params[variable_name] = {'value': value, 'comment': comment}
    