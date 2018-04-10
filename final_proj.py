import requests
import sqlite3
import json
from bs4 import BeautifulSoup
import plotly.plotly as py
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
        # self.box_office = box_office
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
    # print(top_genrelinks)
    for links in top_genre:
        # print(links['href'])
        top_genrelinks.append(links['href'])
    for items in top_genrelinks[:10]:
        baseurl_genre = baseurl[:-1] + items
        # print(baseurl_genre)

    return baseurl_genre

get_topgenre_urls()




def get_movies(genre):
    global movie_list
    beg_url = 'https://www.rottentomatoes.com/top/bestofrt/top_100_'
    end_url = "_movies/"
    url = beg_url + genre + end_url
    # print(url)
    movie_list=[]
    eachgenre_text = make_request_using_cache(url)
    genre_soup = BeautifulSoup(eachgenre_text, 'html.parser')
    list_movies = genre_soup.find('table', {'class': 'table'})
    # print(list_movies)
    list_movies_url = list_movies.find_all('tr')
    # movies_list = []
    for item in list_movies_url[1:]: #---- remove the index
        num_rev = item.find(class_= "right hidden-xs").text #----- number of rev
        # print(num_rev)
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
            # movie = movie_info.find('div', {'id': 'mainColumn'}) ---- commented this out cause of nosefreatu
            # movies_name = movie.find('h1').text.strip()

            for ultag in movie_info.find_all('ul', {'class': 'content-meta info'}):
                for litag in ultag.find_all("li"):
                    titles= litag.find('div', {'class': 'meta-label'}).text.strip()

                    if titles == "Rating:":
                        movie_rated = litag.find('div', {'class': 'meta-value'}).text
                        if len(movie_rated) >1:
                            movie_rating = movie_rated[:2]
                            # print(movie_rating)
                    elif titles == "Genre:":
                        movie_genres = litag.find('div', {'class': 'meta-value'}).text.replace(' ', '').replace('\n', '').split(',')
                        movie_genre = movie_genres[0]
                        # print(movie_genre[0])
                    elif titles == "Directed By:":
                        movie_directors = litag.find('div', {'class': 'meta-value'}).text.strip().split(",")
                        movie_director = movie_directors[0]



                    elif titles == "Runtime:":
                        runtime = litag.find('div', {'class': 'meta-value'}).text.strip().split()
                        movie_runtime = runtime[0]

                    elif titles == "Studio:":
                        movie_studio = litag.find('div', {'class': 'meta-value'}).text.strip()
                        # print(movie_studio)

        each_movie_instance = Movie(name= movie_name, rating= movie_rating, genre= movie_genre, director= movie_director, release_year=year, runtime=movie_runtime, studio=movie_studio, reviews=num_rev)
        movie_list.append(each_movie_instance)




    return movie_list

get_movies("romance")
def create_csv():
    file_name = open("Movies.csv", "w")
    file_name.write("Movie, Genre, Rating, MovieLength, Director, ReleaseYear, Studio, Reviews\n")
    for movies in movie_list:
        Movie = movies.name
        Genre = movies.genre
        Rating = movies.rating
        MovieLength = movies.runtime
        Director = movies.director
        ReleaseYear = movies.release_year
        Studio = movies.studio
        Reviews = movies.reviews
        file_name.write("{}, {}, {}, {}, {}, {}, {}, {}\n".format(Movie,Genre,Rating,MovieLength,Director,ReleaseYear,Studio,Reviews))
    file_name.close()

create_csv()


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
          'NumberReviews' TEXT NOT NULL,
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
          'Genre' TEXT,
          'Rating' TEXT,
          'MovieLength' REAL,
          'Director' TEXT,
          'Studio' TEXT NOT NULL

      );
  '''
  cur.execute(statement) #executing

  conn.commit()
  conn.close()

init_db(DBNAME)
# def insert_row_csv_extra(csv_list):
#     movie_dict = {}
#     movie_id  = 1
#     movies_csv= open(MOVIESCSV)
#     csvReader = csv.reader(movies_csv)
#     csv_list = list(csvReader)
#     del(csv_list[0])
#     for rows in csv_list:
#       movie_dict[rows[0]] = movie_id
#       movie_id +=1
#       print(movie_dict)
    # for keys in movie_dict:



    # print(counts)
# my_dict[row[0]] = id_
#         id_ +=1
# insert_row_csv_extra(MOVIESCSV)

def insert_csv_data(csv_file):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for row in csv_file:
        insertion = (row[0], row[5], row[7])
        statement = 'INSERT INTO "Critics" '
        statement += 'VALUES (NULL, ?, ?, NULL, ?) '
        cur.execute(statement, insertion)
    conn.commit()
# #
def insert_csv_data2(csv_file):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    my_dict = {}
    id_ = 1000
    for row in csv_file:
        insertion = (row[0], row[1], row[2], row[3], row[4], row[6])
        statement = 'INSERT INTO "Movies" '
        statement += 'VALUES (NULL, ?, ?, ?, ?, ?, ?) '
        my_dict[row[0]] = id_
        id_ +=1
        cur.execute(statement, insertion)
    conn.commit()

    for keys in my_dict:
      try:
        cur.execute('UPDATE Critics SET MovieId =' + str(my_dict[keys]) + ' WHERE MovieName =' + '"' + keys + '"')
        cur.execute('UPDATE Movies SET Id =' + str(my_dict[keys]) + ' WHERE MovieName =' + '"' + keys + '"')
      except:
        pass
    conn.commit()

init_db(DBNAME)

#
movies_csv= open(MOVIESCSV)
csvReader = csv.reader(movies_csv)
csv_list = list(csvReader)
del(csv_list[0])
insert_csv_data(csv_list)

movies_csv= open(MOVIESCSV)
csvReader = csv.reader(movies_csv)
csv_list = list(csvReader)
del(csv_list[0])
insert_csv_data2(csv_list)



#romance -- cached
#horror -- cached
#animation -- cached
#drama -- cached
#comedy -- cached
#documentary -- cached
#television -- cached
