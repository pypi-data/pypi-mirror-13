"""This is the "nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists."""
from __future__ import print_function

def print_all_items(items, level=0):
    """This is the standard way to
     include a multiple-line comment in
     your code."""
    for each_line in items:
        if isinstance(each_line, list):
            print_all_items(each_line, level+1)
        else:
            for tab in range(level):
                print("\t", end='')
            print(each_line)

if __name__ == '__main__':
    movies = [
        "The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
         ["Graham Chapman",
         ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

    print_all_items(movies)
