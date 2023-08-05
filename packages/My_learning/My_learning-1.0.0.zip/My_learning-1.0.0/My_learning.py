def my_print(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            my_print(each_item)
        else:
            print(each_item)
