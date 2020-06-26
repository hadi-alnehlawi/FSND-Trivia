import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_username = "postgres"
        self.database_password = "postgres"
        self.database_hostname = "localhost"
        self.database_port = 5432
        self.database_path = "postgres://{}:{}@{}:{}/{}".format(
                            self.database_username, self.database_password,
                            self.database_hostname, self.database_port,
                            self.database_name)
        setup_db(self.app, self.database_path)


# binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation
    and for expected errors.
    """
    request_body = dict(
                    answer="my name is Hadi",
                    category="2",
                    difficulty="2",
                    question="what is your name ????",
                    )

    # GET Test
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = response.get_json()
        self.assertEqual(response.status_code,  200)
        self.assertTrue(data.get('success'))

    def test_get_question_id_15(self):
        response = self.client().get('/questions/15')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)

    def test_get_404_question_id(self):
        response = self.client().get('/questions/220333')
        data = response.get_json()
        self.assertEqual(data.get('error'), 404)

    # POST Test
    def test_post_questions_200(self):
        response = self.client().post('/questions', json=self.request_body)
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])

    def test_post_question_search_term_200(self):
        search_term_dict = dict(searchTerm=self.request_body.get('question'))
        response = self.client().post('/questions/search_term',
                                      json=search_term_dict)
        data = response.get_json()
        self.assertEqual(response.status_code, 200)

    def test_post_question_search_term_404(self):
        search_term_dict = dict(searchTerm="not existed")
        response = self.client().post('/questions/search_term',
                                      json=search_term_dict)
        data = response.get_json()
        self.assertEqual(data['error'], 404)
        self.assertEqual(data["success"], False)
    def test_post_questions_405(self):
        requests_body = dict(
                answer="my name is Hadi",
                category="2",
                difficulty="2",
                question="what is your name ????",
                success=True,
                )
        response = self.client().post('/questions/wrong_uri')
        data = response.get_json()
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)

    # DELETE Test
    def test_delete_questions_200(self):
        question_to_delete = Question.query.first()
        response = self.client().delete('/questions/{0}'.
                                        format(question_to_delete.id))
        data = response.get_json()
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)

    def test_delete_questions_404(self):
        response = self.client().delete('/questions/44444')
        data = response.get_json()
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
