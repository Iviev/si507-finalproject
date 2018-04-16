import unittest
from final_proj import *
import json
import requests



class TestDatabase(unittest.TestCase):
    def setUp(self):
        # get_movies("horror")
        create_csv(get_movies("horror"))
        init_db(DBNAME)
        insert_csv_data(MOVIESCSV)
        insert_csv_data2(MOVIESCSV)


    def test_movies_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT MovieName FROM Movies'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Get Out',), result_list)
        self.assertEqual(len(result_list), 100)

        sql = '''
            SELECT MovieName, Genre, Rating,
                   MovieLength, Director
            FROM Movies
            WHERE Genre=" Classics"
            ORDER BY Rating DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 17)
        self.assertEqual(result_list[0][3], 109.0)

        conn.close()

    def test_critics_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT ReleaseYear
            FROM Critics
            WHERE NumberReviews="60"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((1965,), result_list)
        self.assertEqual(len(result_list), 2)

        sql = '''
            SELECT COUNT(*)
            FROM Critics
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertEqual(count, 100)

        conn.close()

class TestMoviesSearch(unittest.TestCase):
    def setUp(self):
        create_csv(get_movies("horror"))
        init_db(DBNAME)
        insert_csv_data(MOVIESCSV)
        insert_csv_data2(MOVIESCSV)

    def test_command_search(self):
        results = movies_command('movies top=1')
        self.assertEqual(results[0][2], ' Drama')

        results = genres_command('genres number_reviews')
        self.assertEqual(results[1][2], 1984)


        results = compare_command('compare directors top=10')
        self.assertEqual(results[1][2], " Trey Edward Shults")
        self.assertEqual(len(results), 10)
        #
        results = studio_command('studios number_reviews top=5')
        self.assertEqual(results[3][1], 2009)
        self.assertEqual(results[1][0], " Warner-Bros.-Pictures")


class TestMovieInstance(unittest.TestCase):
    def setUp(self):
        create_csv(get_movies("horror"))
        init_db(DBNAME)
        insert_csv_data(MOVIESCSV)
        insert_csv_data2(MOVIESCSV)

    def testConstructor(self):

        m1 = Movie("Delusional Love", "PG", "Romance", "Idaghe", "2018", "120", "Chicago-20th", "100")
        self.assertEqual(m1.name, "Delusional Love")
        self.assertEqual(m1.rating, "PG")
        self.assertEqual(m1.genre, "Romance")
        self.assertEqual(m1.director, "Idaghe")
        self.assertEqual(m1.release_year, "2018")
        self.assertEqual(m1.runtime, "120")
        self.assertEqual(m1.studio, "Chicago-20th")
        self.assertEqual(m1.reviews, "100")


    def test_MovieString(self):
        movies = Movie("Delusional Love", "PG", "Romance", "Idaghe", "2018", "120", "Chicago-20th", "100")
        self.assertEqual(movies.__str__(), "Delusional Love rated PG (2018) directed by Idaghe")









unittest.main()
