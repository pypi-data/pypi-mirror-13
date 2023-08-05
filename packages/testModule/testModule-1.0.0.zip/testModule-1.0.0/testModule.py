def print_lol(theList):
    for ele in theList:
        if isinstance(ele , list):
            print_lol(ele)
        else:
            print(ele)