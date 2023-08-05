def recursive_function(movie_list,level):
    """
    This is a function, it accepts the movie list as an argument.
    :param movie_list:
    :return:
    """
    for each_movie in movie_list:
        if isinstance(each_movie, list):
            recursive_function(each_movie,level)
        else:
            for num in range(level):
                print("\t")
                
            print(each_movie)
