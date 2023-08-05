__author__ = 'Administrator'
'''This is a isinstance.py.'''
movies = ['The Holy Grail',1975,'The Life of Brian',91,['The Meaning of Life',[111,222,333]]]
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print each_item
print_lol(movies)
