"""This is the “nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists"""
import sys
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

def print_lol(theList,indent=False,level=0,fh=sys.stdout):
        
    """This function takes a positional argument called “the_list", which is any
    Python list (of, possibly, nested lists). Each data item in the provided list
    is (recursively) printed to the screen on its own line. A second
    argument called “level" is used to insert tab-stops when a nested list
    is encountered. The 4th Argument is a file output or none to print on screen """
    for item in theList:
        if isinstance(item,list):
            print_lol(item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print ("\t",end='',file=fh)
            print(item,file=fh)

