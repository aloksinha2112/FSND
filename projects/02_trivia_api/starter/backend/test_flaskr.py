import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import false

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        #self.database_name = "trivia_test"
        #self.database_path = "postgresql://{}:{}@{}/{}".format("caryn", "caryn", "localhost:5432",self.database_name)
        self.databse_host = os.getenv('database_host', 'localhost:5432')
        self.database_name = os.getenv('database_name', 'trivia_test')
        self.database_user = os.getenv('database_user', 'caryn')  
        self.database_password = os.getenv('database_password', 'caryn')  
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.database_user, self.database_password, self.databse_host, self.database_name)
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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['categories']) 

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data["total_questions"])
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))
    
    def test_get_paginated_questions_404_error(self):
        res = self.client().get('/questions?page=20')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Page Not Found')
    
    def test_delete_questions(self):
        
        new_question = Question('testquestion', 'testanswer', '1', '1')
        new_question.insert() 

        res = self.client().delete("/questions/" + str(new_question.id))
        data = json.loads(res.data)

        question_tobedeletd = Question.query.filter(Question.id == new_question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], new_question.id)
        self.assertEqual(question_tobedeletd, None)
    
    def test_create_questions(self):
        question = {
            'question':'Which dung beetle was worshipped by the ancient Egyptians?',
            'answer': 'Scarab',
            'difficulty': 4,
            'category': 4
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])    

    def test_search_questions(self):
        search_data = {
            'searchTerm': 'boxer'
        }
        res = self.client().post('/questions/search', json=search_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))    
    
    def test_get_qestionsbycategory(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    def test_get_nextquestion(self):
        question_data = {
            'previous_questions':[],
            'quiz_category' : {
                'type': 'Science',
                'id': 1
            }
        }
        res = self.client().post('/quizzes', json=question_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])   
         
    def test_get_paginated_questions_404_error(self):
        res = self.client().get('/questions?page=20')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)    

    def test_delete_questions_422_not_allowed(self):
        res = self.client().delete('/questions/2222')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False) 

    def test_create_questions_400_validation_error(self):
        new_question = {
            'question': 'test question',
            'answer': 'test answer'
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_get_qestionsbycategory_400_not_exist(self):
        res = self.client().get('/categories/2222/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()