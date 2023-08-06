def print_list(alist):
    for each_item in alist:
       if isinstance(each_item,list):
           print_list(each_item)
       else:
           print(each_item)
