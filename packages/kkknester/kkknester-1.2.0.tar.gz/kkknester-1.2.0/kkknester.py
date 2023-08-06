def print_list(arr, indent=False, level=0):
        for item in arr:
                if isinstance(item,list):
                        print_list(item, indent, level+1)
                else:
                        if indent:
                                for tabs in range(level):
                                        print('\t', end='')
                        print(item)
