import requests
import sqlite3
import json
from bs4 import BeautifulSoup
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import csv
from prettytable import PrettyTable

DBNAME = 'movies.db'
MOVIESCSV = 'Movies.csv'


CACHE_FNAME = "cached_movies.json"
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
    # if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}


def get_unique_key(url):
  return url


def make_request_using_cache(url):
    global header
    unique_ident = get_unique_key(url)


    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        # header = {'User-Agent': 'SI_CLASS'}
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

class Movie():
    def __init__(self, name, rating, genre, director, release_year, runtime, studio, reviews):
        self.name = name
        self.rating = rating
        self.genre = genre
        self.director = director
        self.release_year = release_year
        self.runtime = runtime
        self.studio = studio
        self.reviews = reviews


    def __str__(self):
        return "{} rated {} ({}) directed by {}".format(self.name,self.rating,self.release_year,self.director)



baseurl = 'https://www.rottentomatoes.com/'
page_text = requests.get(baseurl).text
page_soup = BeautifulSoup(page_text, 'html.parser')
content_div = page_soup.find(class_="navbar-nav col-sm-11 hidden-xs")
movie_search= content_div.find(class_="row-sameColumnHeight")
movie_searchbar = movie_search.find(class_="col-xs-3 subnav")
movie_search_div = movie_searchbar.find(class_="innerSubnav")
top_movies_link= movie_search_div.find(class_="unstyled articleLink")
top_movies_end_url =movie_search_div.find("a")["href"]



def get_topgenre_urls():
    global top_genrelinks
    topmovies_baseurl= baseurl[:-1]+ top_movies_end_url
    topmovies_pagetext = requests.get(topmovies_baseurl).text
    topmovies_soup = BeautifulSoup(topmovies_pagetext, 'html.parser')
    topmovies_content = topmovies_soup.find('ul', {'class': 'genrelist'}) #undo to get to container masonry blah blah
    top_genre = topmovies_content.find_all('a', {'class': 'articleLink unstyled'})
    top_genrelinks = []
    for links in top_genre:
        top_genrelinks.append(links['href'])
    for items in top_genrelinks[:10]:
        baseurl_genre = baseurl[:-1] + items


    return baseurl_genre

# get_topgenre_urls()




def get_movies(genre):
    # global movie_list
    beg_url = 'https://www.rottentomatoes.com/top/bestofrt/top_100_'
    end_url = "_movies/"
    url = beg_url + genre + end_url
    movie_list=[]
    eachgenre_text = make_request_using_cache(url)
    genre_soup = BeautifulSoup(eachgenre_text, 'html.parser')
    list_movies = genre_soup.find('table', {'class': 'table'})
    list_movies_url = list_movies.find_all('tr')
    for item in list_movies_url[1:]: #---- remove the index
        num_rev = item.find(class_= "right hidden-xs").text #----- number of rev
        item_link = item.find("a")
        if item_link:
            names = item.find('a').text
            movie_link = item.find("a")["href"]
            split_name = names[:-6]
            movies_name = split_name.strip().split(",")
            movie_name = movies_name[0]


            year = names[-5:-1]
            movie_url = baseurl[:-1] + movie_link
            movie_info_text = make_request_using_cache(movie_url)
            movie_info = BeautifulSoup(movie_info_text, "html.parser")


            for ultag in movie_info.find_all('ul', {'class': 'content-meta info'}):
                for litag in ultag.find_all("li"):
                    titles= litag.find('div', {'class': 'meta-label'}).text.strip()

                    if titles == "Rating:":
                        movie_rated = litag.find('div', {'class': 'meta-value'}).text
                        if len(movie_rated) >1:
                            movie_ratings = movie_rated.split() #---was [;2]
                            movie_rating = movie_ratings[0]
                            # print(movie_rating)
                    elif titles == "Genre:":
                        movie_genres = litag.find('div', {'class': 'meta-value'}).text.replace(' ', '').replace('\n', '').split(',')
                        movie_genre = movie_genres[0]

                    elif titles == "Directed By:":
                        movie_directors = litag.find('div', {'class': 'meta-value'}).text.strip().split(",")
                        movie_director = movie_directors[0]



                    elif titles == "Runtime:":
                        runtime = litag.find('div', {'class': 'meta-value'}).text.strip().split()
                        movie_runtime = runtime[0]

                    elif titles == "Studio:":
                        movie_studio = litag.find('div', {'class': 'meta-value'}).text.strip().replace(" ", "-")
                        # print(movie_studio)

        each_movie_instance = Movie(name= movie_name, rating= movie_rating, genre= movie_genre, director= movie_director, release_year=year, runtime=movie_runtime, studio=movie_studio, reviews=num_rev)
        movie_list.append(each_movie_instance)




    return movie_list

def create_csv(movie_list):

    file_name = open("Movies.csv", "w")
    file_name.write("Movie, MovieId, Genre, Rating, MovieLength, Director, ReleaseYear, Studio, Reviews\n")
    counter = 1000
    for movies in movie_list:
      counter += 1
      MovieId = counter
      Movie = movies.name
      Genre = movies.genre
      Rating = movies.rating
      MovieLength = movies.runtime
      Director = movies.director
      ReleaseYear = movies.release_year
      Studio = movies.studio
      Reviews = movies.reviews
      file_name.write("{}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(Movie,MovieId,Genre,Rating,MovieLength,Director,ReleaseYear,Studio,Reviews))
    file_name.close()



def init_db(db_name):

  conn = sqlite3.connect('movies.db')
  cur = conn.cursor()

  # Drop tables
  statement = '''
      DROP TABLE IF EXISTS 'Critics';
  '''
  cur.execute(statement)
  conn.commit()

  statement = '''
      CREATE TABLE 'Critics' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'MovieName' TEXT NOT NULL,
          'ReleaseYear' INTEGER,
          'MovieId' INTEGER,
          'NumberReviews' REAL,
          FOREIGN KEY (MovieId) REFERENCES Movies(Id)

      );
  '''
  cur.execute(statement)
  conn.commit()
  # conn.close()


  statement = '''
      DROP TABLE IF EXISTS 'Movies';
  '''
  cur.execute(statement)
  conn.commit()


  statement = '''
      CREATE TABLE 'Movies' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'MovieName' TEXT NOT NULL,
          'Genre' TEXT NOT NULL,
          'Rating' TEXT NOT NULL,
          'MovieLength' REAL,
          'Director' TEXT,
          'Studio' TEXT NOT NULL

      );
  '''
  cur.execute(statement) #executing

  conn.commit()
  conn.close()


def insert_csv_data(csv_file):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    movies_csv= open(csv_file)
    csvReader = csv.reader(movies_csv)
    csv_list = list(csvReader)
    del(csv_list[0])
    movies_csv.close()
    for row in csv_list:
        insertion = (row[0], row[6], row[8])
        statement = 'INSERT INTO "Critics" '
        statement += 'VALUES (NULL, ?, ?, NULL, ?) '
        cur.execute(statement, insertion)
    conn.commit()

def insert_csv_data2(csv_file):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    movies_csv= open(csv_file)
    csvReader = csv.reader(movies_csv)
    csv_list = list(csvReader)
    del(csv_list[0])
    movies_csv.close()
    my_dict = {}
    id_ = 1001

    for row in csv_list:
        insertion = (row[1], row[0], row[2], row[3], row[4], row[5], row[7])
        statement = 'INSERT INTO "Movies" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?) '
        my_dict[row[0]] = id_
        id_ +=1
        cur.execute(statement, insertion)
    conn.commit()

    for keys in my_dict:
      try:
        cur.execute('UPDATE Critics SET MovieId =' + str(my_dict[keys]) + ' WHERE MovieName =' + '"' + keys + '"')

      except:
        pass
    conn.commit()


# print("----------TABLES HERE----------")
def movies_command(command):
  global result_value
  global director_list
  global movielength_list
  global moviereview_list
  global movie_rating_list
  movie_rating_list  = []
  movielength_list = []
  moviereview_list = []
  conn = sqlite3.connect(DBNAME)
  cur = conn.cursor()
  statement1 = 'SELECT Movies.MovieName, Movies.Rating, Movies.Genre, c.ReleaseYear, Movies.MovieLength, c.NumberReviews '
  statement2 = 'FROM Movies '
  join_statement1 = 'JOIN Critics as c ON Movies.Id = c.MovieId '
  join_statement2 = ''
  filming_studio = ''
  year = ''
  group_by = ''
  order_by = 'ORDER BY Movies.MovieLength '
  top_bottom = 'DESC ' #-- changed this from desc
  limit = 'LIMIT 10'


  response2 = command.split()
  for words in response2:
    if "filming_studio" in words:
      statement1 = 'SELECT Movies.MovieName, Movies.Studio, Movies.Genre, c.ReleaseYear, Movies.MovieLength, c.NumberReviews '
      split = words.split("=")
      studio_name = split[1]
      join_statement1 = 'JOIN Critics as c ON Movies.Id = c.MovieId '
      filming_studio = 'WHERE Movies.Studio = " ' + studio_name + '" '


    if "year" in words:
      split = words.split("=")
      release_year = split[1]
      join_statement1 = 'JOIN Critics as c ON Movies.Id = c.MovieId '
      year = 'WHERE c.ReleaseYear = " ' + release_year + '" '


    if "ratings" in words: #take review out
      statement1 = 'SELECT Movies.MovieName, Movies.Rating, COUNT(*), c.ReleaseYear, Movies.MovieLength, c.NumberReviews '
      group_by = 'GROUP BY Movies.Rating '
      limit = ''
    #create an if rating that that pulls up ratings and a count of movies in that genre---us db browser first

    if "top" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = 'DESC '
      limit = 'LIMIT "' + limit_no + '" '

    if "bottom" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = ''
      limit = 'LIMIT "' + limit_no + '" '


  cur.execute(statement1 + statement2 + join_statement1 + join_statement2 + filming_studio + year + group_by + order_by + top_bottom + limit)
  # print(statement1 + statement2 + join_statement1 + join_statement2 + filming_studio + year + order_by + top_bottom + limit)
  beautiful_table = PrettyTable()
  beautiful_table.field_names = ["MovieName", "Studio/Rating", "Genre/Count", "ReleaseYear", "MovieLength", "NumberReviews"]
  for row in cur:
      beautiful_table.add_row(row)
      director_row = row[2]
      movielength_row = row[4]
      moviereview_row = row[5]
      movielength_list.append(movielength_row)
      moviereview_list.append(moviereview_row)
      movie_rating_row = row[1]
      movie_rating_list.append(movie_rating_row)

  print(beautiful_table)
  result = cur.execute(statement1 + statement2 + join_statement1 + join_statement2 + filming_studio + year + group_by + order_by + top_bottom + limit)
  # result_value = result.fetchall()
  return result.fetchall()


def genres_command(command):
  global plot_genre_list
  global plot_genre_reviews
  plot_genre_list = []
  plot_genre_reviews = []
  conn = sqlite3.connect(DBNAME)
  cur = conn.cursor()
  statement1 = 'SELECT Movies.MovieName, Movies.Genre, c.ReleaseYear, ROUND(AVG(c.NumberReviews), 1) '
  statement2 = 'FROM Movies '
  join_statement1 = 'JOIN Critics as c ON Movies.Id = c.MovieId '
  genre = ''
  year = ''
  ratings = ''
  group_by = 'GROUP BY Movies.Genre '
  order_by = 'ORDER BY Movies.MovieLength '
  top_bottom = 'DESC ' #-- changed this from desc
  limit = 'LIMIT 20'

  response2 = command.split()
  for words in response2:
    if "category" in words:
      split_info = response2[1]
      split_name = split_info.split("=")
      genre_name = split_name[1]
      genre = 'WHERE Movies.Genre = " ' + genre_name + '" '
      group_by = 'GROUP BY Movies.Genre '


    if "number_reviews" in words:
        statement1 = 'SELECT Movies.MovieName, Movies.Genre, c.ReleaseYear, ROUND(AVG(c.NumberReviews), 1) '
        order_by = 'ORDER BY AVG(c.NumberReviews) '

    if "ratings" in words:
      split = words.split("=")
      rating_movie= split[1].upper()
      ratings = 'WHERE Movies.Rating = " ' + rating_movie + '" '
      order_by = 'ORDER BY c.NumberReviews ' #this line only original
      limit = ''

    if "top" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = 'DESC '
      limit = 'LIMIT "' + limit_no + '" '

    if "bottom" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = ''
      limit = 'LIMIT "' + limit_no + '" '


  cur.execute(statement1 + statement2 + join_statement1 + genre + year + ratings + group_by + order_by + top_bottom + limit)
  # print(statement1 + statement2 + join_statement1 + genre + year + ratings + group_by + order_by + top_bottom + limit)
  beautiful_table = PrettyTable()
  beautiful_table.field_names = ["MovieName", "Genre", "Year", "AggregateValue"]
  for row in cur:
    genre_list_row = row[1]
    plot_genre_list.append(genre_list_row)
    genre_review_row = row[3]
    plot_genre_reviews.append(genre_review_row)
    beautiful_table.add_row(row)
  print(beautiful_table)
  result = cur.execute(statement1 + statement2 + join_statement1 + genre + year + ratings + group_by + order_by + top_bottom + limit)
  return result.fetchall()

def studio_command(command):
  global plot_studio_list
  global plot_count_review
  global plot_average_review
  plot_studio_list = []
  plot_count_review = []
  plot_average_review = []
  conn = sqlite3.connect(DBNAME)
  cur = conn.cursor()
  statement1 = 'SELECT Movies.Studio, c.ReleaseYear, Movies.Rating, COUNT(c.NumberReviews), ROUND(AVG(c.NumberReviews)) '
  statement2 = 'FROM Movies '
  join_statement1 = 'JOIN Critics as c ON c.MovieId = Movies.Id '
  genre = ''
  year = ''
  ratings = ''
  group_by = 'GROUP BY Movies.Studio '
  having = ''
  order_by = 'ORDER BY c.ReleaseYear '
  top_bottom = 'DESC '
  limit = 'LIMIT 30'


  response2 = command.split()
  for words in response2: #how many movies were in top 100 in a specific year
    if "year" in words:
      split = words.split("=")
      release_year = split[1]
      year = 'WHERE c.ReleaseYear = " ' + release_year + '" '

    if "ratings" in words:
      statement1 = 'SELECT DISTINCT Movies.Studio, c.ReleaseYear, Movies.Rating, COUNT(c.NumberReviews), ROUND(AVG(c.NumberReviews)) '
      split = words.split("=")
      rating_movie= split[1].upper()
      ratings = 'WHERE Movies.Rating = " ' + rating_movie + '" '
      limit = ''

    if "genre" in words:
      split = words.split("=")
      genre_name = split[1]
      genre = 'WHERE Movies.Genre = " ' + genre_name + '" '


    if "number_reviews" in words:
      order_by = 'ORDER BY COUNT(c.ReleaseYear) '
      group_by = 'GROUP BY Movies.Studio '

    if "top" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = 'DESC '
      limit = 'LIMIT "' + limit_no + '" '

    if "bottom" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = ''
      limit = 'LIMIT "' + limit_no + '" '

  cur.execute(statement1 + statement2 + join_statement1 + genre + year + ratings + group_by + having + order_by + top_bottom + limit)
  # print(statement1 + statement2 + join_statement1 + genre + year + ratings + group_by + order_by + top_bottom + limit)
  beautiful_table = PrettyTable()
  beautiful_table.field_names = ["MovieStudio", "ReleaseYear", "Rating", "Count", "Average"]
  for row in cur:
    studio_list_row = row[0]
    plot_studio_list.append(studio_list_row)
    count_review_row = row[3]
    plot_count_review.append(count_review_row)
    average_review_row = row[4]
    plot_average_review.append(average_review_row)
    beautiful_table.add_row(row)
  print(beautiful_table)
  result = cur.execute(statement1 + statement2 + join_statement1 + genre + year + ratings + group_by + having + order_by + top_bottom + limit)
  return result.fetchall()

def compare_command(command):
  global director_list
  global director_movielength_list
  global director_moviereview_list
  director_list = []
  director_movielength_list = []
  director_moviereview_list = []
  conn = sqlite3.connect(DBNAME)
  cur = conn.cursor()
  statement1 =   statement1 = 'SELECT Movies.MovieName, Movies.Studio, Movies.Director, c.ReleaseYear, Movies.MovieLength, c.NumberReviews '
  statement2 = 'FROM Movies '
  join_statement1 = 'JOIN Critics as c ON Movies.Id = c.MovieId '
  join_statement2 = ''
  filming_studio = ''
  year = ''
  group_by = ''
  order_by = 'ORDER BY Movies.MovieLength '
  top_bottom = 'DESC ' #-- changed this from desc
  limit = 'LIMIT 10'


  response2 = command.split()
  for words in response2:
    if "directors" in words:
      # print("here")
      order_by = 'ORDER BY c.ReleaseYear '

    if "top" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = 'DESC '
      limit = 'LIMIT "' + limit_no + '" '

    if "bottom" in words:
      split = words.split("=")
      limit_no = split[1]
      top_bottom = ''
      limit = 'LIMIT "' + limit_no + '" '


  cur.execute(statement1 + statement2 + join_statement1 + join_statement2 + filming_studio + year + group_by + order_by + top_bottom + limit)
  # print(statement1 + statement2 + join_statement1 + join_statement2 + filming_studio + year + order_by + top_bottom + limit)
  beautiful_table = PrettyTable()
  beautiful_table.field_names = ["MovieName", "Studio", "Director", "ReleaseYear", "MovieLength", "NumberReviews"]
  for row in cur:
    beautiful_table.add_row(row)
    director_row = row[2]
    director_list.append(director_row)
    director_movielength_row = row[4]
    director_moviereview_row = row[5]
    director_movielength_list.append(director_movielength_row)
    director_moviereview_list.append(director_moviereview_row)
  print(beautiful_table)
  result = cur.execute(statement1 + statement2 + join_statement1 + join_statement2 + filming_studio + year + group_by + order_by + top_bottom + limit)
  return result.fetchall()


def process_command(command, debug=False):
  # global visualize

  conn = sqlite3.connect(DBNAME)
  cur = conn.cursor()
  if command.split()[0] == "movies":
    movies_command(command)
    if not debug:
      visualize = input("Do you want to visualize a breakdown of Movies Studios/Ratings by Runtime and number of reviews: ")
      if visualize == "yes":
        get_donutchart_movies()
      else:
        pass
      # return movies_command(command)

  if command.split()[0] == "genres":
    genres_command(command)
    if not debug:
      visualize = input("Do you want to visualize a breakdown of Movies Genres by number of reviews: ")
      if visualize == "yes":
        get_pie_chart_genre()
      else:
        pass

  if command.split()[0] == "studios":
    studio_command(command)
    visualize = input("Do you want to visualize a breakdown of Movies Studios Average reviews and number of reviews: ")
    if not debug:
      if visualize == "yes":
        get_rotated_barchart_studios()
      else:
        pass

  if command.split()[0] == "compare":
    compare_command(command)
    visualize = input("Do you want to visualize a breakdown of Directors based on reviews and length of the movies they directed: ")
    if not debug:
      if visualize == "yes":
        get_dotplot_director()
      else:
        pass


# print("-----------------------------------PLOTLY FUNCTIONS---------------------------------------")

def get_pie_chart_genre():
  labels = plot_genre_list
  values = plot_genre_reviews

  trace = go.Pie(labels=labels, values=values)

  py.plot([trace], filename='Pie_Chart_genre')

def get_rotated_barchart_studios():

  trace0 = go.Bar(
    x= plot_studio_list,
    y= plot_count_review,
    name='Count reviews',
    marker=dict(
        color='rgb(49,130,189)' #was 49, 130, 189
    )
  )
  trace1 = go.Bar(

      x= plot_studio_list,
      y= plot_average_review,
      name='Average Reviews',
      marker=dict(
          color='rgb(190,190,190)', #was 204
      )
  )

  data = [trace0, trace1]
  layout = go.Layout(
      xaxis=dict(tickangle=-45),
      barmode='group',
  )

  fig = go.Figure(data=data, layout=layout)
  py.plot(fig, filename='angled-text-bar')

def get_dotplot_director():
  trace1 = {"x": director_moviereview_list,
          "y": director_list,
          "marker": {"color": "pink", "size": 12},
          "mode": "markers",
          "name": "Moviereviews",
          "type": "scatter"
  }

  trace2 = {"x": director_movielength_list,
            "y": director_list,
            "marker": {"color": "blue", "size": 12},
            "mode": "markers",
            "name": "MovieLength",
            "type": "scatter",
  }

  data = Data([trace1, trace2])
  layout = {"title": "Breakdown of Movies by Directors based on Runtime and Reviews",
            "xaxis": {"title": "Runtime/Reviews", },
            "yaxis": {"title": "Directors"}}

  fig = Figure(data=data, layout=layout)
  py.plot(fig, filenmae='basic_dot-plot')

def get_donutchart_movies():
  fig = {
  "data": [
    {
      "values": movielength_list,
      "labels": movie_rating_list,
      "domain": {"x": [0, .48]},
      "name": "Movie Length",
      "hoverinfo":"label+percent+name",
      "hole": .4,
      "type": "pie"
    },
    {
      "values": moviereview_list,
      "labels": movie_rating_list,
      "text":"Rev",
      "textposition":"inside",
      "domain": {"x": [.52, 1]},
      "name": "Number of Reviews",
      "hoverinfo":"label+percent+name",
      "hole": .4,
      "type": "pie"
    }],
  "layout": {
      "title":"Breakdown of Movie ratings by runtime and reviews",
      "annotations": [
          {
              "font": {
                  "size": 20
              },
              "showarrow": False,
              "text": "Runtime",
              "x": 0.20,
              "y": 0.5
          },
          {
              "font": {
                  "size": 20
              },
              "showarrow": False,
              "text": "Reviews",
              "x": 0.8,
              "y": 0.5
          }
      ]
    }
  }
  py.plot(fig, filename='donut')


def load_help_text():
  with open('help.txt') as f:
    return f.read()


commands_list = ["horror", "drama", "romance", "documentary", "television"]
commands_list2 = ["movies", "genres", "studios", "compare"]
commands_list3 = ["year", "filming_studio", "ratings", "genre", "top", "bottom", "category", "number_reviews", "directors"] #--original

# # Part 3: Implement interactive prompt. We've started for you!
def interactive_prompt():
  help_text = load_help_text()
  response = ''
  while response != 'exit':
    response = input('Enter search category: ')
    if response == "exit":
        break
    if response == 'help':
        print(help_text)
        continue
    if response == '':
        continue
    if response not in commands_list:
      print("Command not found: " + response)
      continue
    if response in commands_list:
      create_csv(get_movies(response))
      insert_csv_data(MOVIESCSV)
      insert_csv_data2(MOVIESCSV)
      response2 = ''
      while response2 != 'exit':
        response2 = input('Enter a command: ')
        if response2 == "exit":
          break
        if response2 == '':
          continue
        split_response2 = response2.split()
        if split_response2[0] not in commands_list2:
          print("Command not found: " + response2)
          continue

        if len(split_response2) >= 2:
            bad_command = False
            for i in split_response2[1:]:
              if "=" in i:
                i = i.split("=")[0]
                if i not in commands_list3:
                  print("Command not found: " + response2)
                  bad_command = True
                  break
              else:
                if i not in commands_list3:
                  print("Not a valid command: " + response2)
                  bad_command = True
                  break

            if bad_command:
                continue

        process_command(response2)





if __name__=="__main__":
  get_topgenre_urls()
  init_db(DBNAME)
  interactive_prompt()
