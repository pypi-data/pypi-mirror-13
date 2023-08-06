"""This is the nester.py module"""
def mov_sepre(name_list,level=0):
    """This function is just for test"""
    for each in name_list:
        if isinstance(each,list):
            mov_sepre(each,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each)
