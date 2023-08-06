from yac.lib.file import get_file_contents

def apply_stemplate(string_w_variables, template_variables):

    for key in template_variables:
        if 'value' in template_variables[key]:
            variable_value = template_variables[key]['value']
            if (type(variable_value) == str or type(variable_value) == unicode):
                to_replace = "{{%s}}"%key            
                string_w_variables = string_w_variables.replace(to_replace,str(variable_value))

    return string_w_variables

def apply_ftemplate(file_w_variables, template_variables):

    # read file into string
    string_w_variables = get_file_contents(file_w_variables)

    return apply_stemplate(string_w_variables, template_variables)