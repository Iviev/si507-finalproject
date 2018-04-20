# si507-finalproject

Application
This program scrapes and crawls multiple pages on the rotten tomatoes website to retrieve the Top 100 movies for each genre.
This application accepts user input and returns the Top 100 movies in the category
searched by the user.
The user can search one of the following genres:
horror, drama, romance, documentary, television. (lower case)
This returns a list of the top 100 in the genre specified by the user. I implemented a class called "Movie"
This class has attributes such as name, rating, genre, director, release_year, runtime, studio, reviews.
I implemented a cache using the unique url of the genre categories.
I used this class to create instances of each of the top 100 movies, after doing this I create a csv file using each of these
attributes as columns in the file.

Database:
I created two tables, A "Movies" and "Critics" table using the "MovieId" as a foreign key in the Critics table.
I populated this database with the information from the csv file. This database is populated based on the users input, so if the user
specifies "romance" as their genre, it will repopulate the csv and the database with the top 100 movies in the romance genre.

Commands:

Search categories available: horror, romance, drama, documentary, television (lower case)
Sample commands:
 -movies year=2012 top=10
 -genres number_reviews
 -studios rating=PG top=5
 -compare directors top=10
Commands available:

Movies
	Description: Lists Movies, according the specified parameters.

	Options:
		* filming_studio|year|ratings|[default: none]
		Description:
			-	filming_studio: Limits the list by the me of studio specified by user
        When searching name of studio use "-" in between each word of the studio name (For example "Universal-Pictures")
			- year: Specifies a year within which to limit the results
			-ratings: Specifies whether to limit by the rating of the movie(PG)

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

		* the user has the option to visualize information based on their search query

Genres
	Description: Lists Movies and genres according to the specified parameters.

	Options:
		* category=<Genre>|number_reviews|rating<PG-13>[default: none]
		Description:
			- category: Limits the result to one genre as specified by user.
			- number_reviews: Specifies the Numbers of reviews for all genres and order by
				average number of reviews for each genre.
			- ratings: Limits the results to the rating specified by user (PG,PG-13,R)

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

		* the user has the option to visualize information based on their search query

Studios
	Description: Lists movie studios according to specified parameters.

	Options:
		* year|ratings|genre [default:none]
		Description:
			- year: Specifies a year within which to limit the results.
			- ratings: Limits the results to the rating specified by user (PG,PG-13,R)
			- genre: Limits the results to the genre specified by user (Classics)

		* number_reviews [default:none]
		Description: Specifies whether to sort and order by the number of reviews each studio received and the number of movies they released.

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

		* the user has the option to visualize information based on their search query

Compare
	Description: Lists movie directors according to specified parameters.

	Options:
		* directors [default:directors]
		Description: Specifies whether to select movies based on directors
		and order by the release year of the movie

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

		* the user has the option to visualize information based on their search query

Visualization:
I used a bar chart, donut chart, dot plot chart and a pie chart to takes information from user query and presents a visual
representation of them. 

Unittesting:
I created 3 classes of unit test.
I tested my Database and the tables.
I tested each of my commands.
I tested my class function.
