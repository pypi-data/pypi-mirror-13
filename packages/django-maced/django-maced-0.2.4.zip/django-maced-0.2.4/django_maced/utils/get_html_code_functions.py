# TEXT
def get_items_html_code_for_text(item_name, action_type, field_html_name, field_name):
    if action_type == "merge":
        return get_merge_html_code_for_text(item_name, field_html_name, field_name)

    html_code = "<b>" + field_html_name + ": </b>"
    html_code += '<input type="text" class="form-control" id="' + action_type + "-" + item_name + "-" + field_name + '-input" '

    if action_type == "delete" or action_type == "clone" or action_type == "info":
        html_code += "disabled "

    html_code += "/>"

    return html_code


def get_merge_html_code_for_text(item_name, field_html_name, field_name):
    # Create row name
    html_code = "<tr>"
    html_code += "<th>" + field_html_name + ": </th>"

    # Create left panel
    html_code += '<td><input type="text" class="form-control" id="merge-' + item_name + "1-" + field_name + '-input" disabled /></td>'

    # Create middle panel
    html_code += '<td><input type="text" class="form-control" id="merge-' + item_name + "-" + field_name + '-input" /></td>'

    # Create right panel for merge
    html_code += '<td><input type="text" class="form-control" id="merge-' + item_name + "2-" + field_name + '-input" disabled /></td>'

    html_code += "</tr>"

    return html_code


# COLOR
def get_items_html_code_for_color(item_name, action_type, field_html_name, field_name):
    if action_type == "merge":
        return get_merge_html_code_for_color(item_name, field_html_name, field_name)

    html_code = "<b>" + field_html_name + ": </b>"
    html_code += '<input type="color" id="' + action_type + "-" + item_name + "-" + field_name + '-input" value="#00FF00" '

    if action_type == "delete" or action_type == "clone" or action_type == "info":
        html_code += "disabled "

    html_code += "/>"

    return html_code


def get_merge_html_code_for_color(item_name, field_html_name, field_name):
    # Create row name
    html_code = "<tr>"
    html_code += "<th>" + field_html_name + ": </th>"

    # Create left panel
    html_code += '<td><input type="color" id="merge-' + item_name + "1-" + field_name + '-input" value="#00FF00" disabled /></td>'

    # Create middle panel
    html_code += '<td><input type="color" id="merge-' + item_name + "-" + field_name + '-input" value="#00FF00" /></td>'

    # Create right panel for merge
    html_code += '<td><input type="color" id="merge-' + item_name + "2-" + field_name + '-input" value="#00FF00" disabled /></td>'

    html_code += "</tr>"

    return html_code


# SELECT
def get_items_html_code_for_select(item_name, action_type, field_html_name, field_name, options_info):
    options_html_code = get_html_code_for_options(options_info)

    if action_type == "merge":
        return get_merge_html_code_for_select(item_name, field_html_name, field_name, options_html_code)

    html_code = "<b>" + field_html_name + ": </b>"
    html_code += '<select class="form-control" id="' + action_type + "-" + item_name + "-" + field_name + '-input" '

    if action_type == "delete" or action_type == "clone" or action_type == "info":
        html_code += "disabled "

    html_code += ">" + options_html_code + "</select>"

    return html_code


def get_merge_html_code_for_select(item_name, field_html_name, field_name, options_html_code):
    # Create row name
    html_code = "<tr>"
    html_code += "<th>" + field_html_name + ": </th>"

    # Create left panel
    html_code += '<td><select class="form-control" id="merge-' + item_name + "1-" + field_name + '-input" disabled >' + options_html_code + "</select></td>"

    # Create middle panel
    html_code += '<td><select class="form-control" id="merge-' + item_name + "-" + field_name + '-input" disabled >' + options_html_code + "</select></td>"

    # Create right panel for merge
    html_code += '<td><select class="form-control" id="merge-' + item_name + "2-" + field_name + '-input" disabled >' + options_html_code + "</select></td>"

    html_code += "</tr>"

    return html_code


# OPTIONS FOR SELECT
def get_html_code_for_options(options_list):
    html_code = ""

    for i in range(len(options_list)):
        html_code += '<option value="' + str(options_list[i][0]) + '"> ' + str(options_list[i][1]) + " </option>"

    return html_code