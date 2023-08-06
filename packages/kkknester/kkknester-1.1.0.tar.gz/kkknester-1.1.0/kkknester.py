def print_list(arr, level):
        for item in arr:
                if isinstance(item,list):
                        print_list(item, level+1)
                else:
                        for tabs in range(level):
                                print('\t', end='')
                        print(item)
