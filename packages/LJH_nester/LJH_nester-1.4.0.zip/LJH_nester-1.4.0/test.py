# This is my module for displaye a multiple layers list
def print_lol(param, indent = False,tabStop = 0):
    if isinstance(param, list):
        for inner_list in param:
            print_lol(inner_list, indent, tabStop + 1)
    else:
        if indent:
            for tmpNum in range(tabStop-1):
                print("\t", end='')
        print(param)
