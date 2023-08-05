def print_lol(this_list):
    for each_element in this_list:
        if isinstance(each_element,list):
            print_lol(each_element)
        else:
            print(each_element)
