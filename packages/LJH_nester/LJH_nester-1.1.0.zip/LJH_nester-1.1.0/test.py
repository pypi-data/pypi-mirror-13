# This is my module for displaye a multiple layers list
def print_lol(param, tabStop):
    if isinstance(param, list):
        for inner_list in param:
            print_lol(inner_list, tabStop + 1)
    else:
        for tmpNum in range(tabStop-1):
            print("\t", end='')
        print(param)
