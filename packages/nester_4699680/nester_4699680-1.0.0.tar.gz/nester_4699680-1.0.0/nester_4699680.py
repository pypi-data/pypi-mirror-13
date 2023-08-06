def print_list(movies):
    for each_movie in movies:
    	if isinstance(each_movie,list):
    		print_list(each_movie)
    	else:
    		print(each_movie)

