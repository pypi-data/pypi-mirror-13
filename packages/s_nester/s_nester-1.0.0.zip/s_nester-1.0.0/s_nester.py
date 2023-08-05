"""This is the “nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists"""
##for movie in movies:
##    if isinstance(movie,list):
##        for mov in movie:
##            if isinstance(mov,list):
##                for mo in mov:
##                    print (mo)    
##            else:
##                print(mov)
##    else:
##        print (movie)

def print_lol(theList):
        
    """This function takes a positional argument called “the_list", which is any
    Python list (of, possibly, nested lists). Each data item in the provided list
    is (recursively) printed to the screen on its own line."""
    for item in theList:
        if isinstance(item,list):
            print_list(item)
        else:
            print(item)

