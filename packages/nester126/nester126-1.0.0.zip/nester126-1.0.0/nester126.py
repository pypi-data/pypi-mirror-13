"""This is the nester.py module"""
def mov_sepre(name_list):
    """This function is just for test"""
    for each in name_list:
        if isinstance(each,list):
            mov_sepre(each)
        else:
            print(each)
