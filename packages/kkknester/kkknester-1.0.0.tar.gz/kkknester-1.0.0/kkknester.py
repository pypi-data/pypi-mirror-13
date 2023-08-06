def print_list(arr):
        for item in arr:
                if isinstance(item,list):
                        print_list(item)
                else:
                        print(item)
