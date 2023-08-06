"""This is the nester.py module"""
def mov_sepre(name_list,indent=False，level):
    """This function is just for test"""
    for each in name_list:
        if isinstance(each,list):
            mov_sepre(each,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each)
