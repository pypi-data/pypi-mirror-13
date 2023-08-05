def each_movie(movie_list, level=0):
    if isinstance(movie_list, list):
        for items in movie_list:
            each_movie(items, level+1)
            #print items
    else:
        for tab_stop in range(level):
            print "\t"
        print movie_list 
