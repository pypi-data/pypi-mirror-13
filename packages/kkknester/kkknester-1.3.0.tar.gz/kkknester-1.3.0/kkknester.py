def print_list(arr, indent=False, level=0, fh=sys.stdout):
        for item in arr:
                if isinstance(item,list):
                        print_list(item, indent, level+1, fh)
                else:
                        if indent:
                                print('\t'*level, end='')
                        print(item)
