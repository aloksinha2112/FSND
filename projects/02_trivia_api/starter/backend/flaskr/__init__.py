import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*": {"origins": "*"}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type, Authorization"
    )
    response.headers.add(
        "Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTION"
    )
    return response  
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}
    
    return jsonify({
          'success': True,
          'status': 200,
          'categories': formatted_categories,
      })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}
    total_questions = Question.query.count()
    items_limit = request.args.get('limit', 10, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1
    questions = \
              Question.query.order_by(
                  Question.id
              ).limit(items_limit).offset(current_index * items_limit).all()
    paginated_questions = [question.format() for question in questions]
    if len(paginated_questions) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'status': 200,
        'questions': paginated_questions,
        'total_questions': total_questions,
        'categories': formatted_categories
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):   
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
          abort(404)
      question.delete()    
      return jsonify({
        'success': True,
        'status': 200,
        'deleted': question_id  
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    if request.data:
      body = request.get_json()
      question = body.get('question', None)
      answer = body.get('answer', None)
      category = body.get('category', None)
      difficulty = body.get('difficulty', None)

      if (question is None) or (answer is None) or (category is None) or (difficulty is None):
        return abort(400)

      try:
        new_question = Question(question, answer, category, difficulty)
        new_question.insert()  
      
        return jsonify({
          'success': True,
          'status': 200,
          'question': new_question.format()
        })
      except:
        return abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    if request.data:
      body = request.get_json()
      searchterm = body.get('searchTerm', None)
      
      if (searchterm is None):
        return abort(400)

      try:
        #questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchterm))).all()
        items_limit = request.args.get('limit', 10, type=int)
        selected_page = request.args.get('page', 1, type=int)
        current_index = selected_page - 1

        questions = \
                  Question.query.filter(
                Question.question.ilike('%{}%'.format(searchterm))).order_by(
                      Question.id
                  ).limit(items_limit).offset(current_index * items_limit).all()
        paginated_questions = [question.format() for question in questions]
        #paginated_questions = paginated(request, questions)

        return jsonify({
          'success': True,
          'status': 200,
          'questions': paginated_questions,
          'total_questions': len(paginated_questions)
        })
      except:
        return abort(400)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_qestionsbycategory(category_id):
    #questions = Question.query.filter(Question.category == str(category_id)).all()
    #paginated_questions = paginated(request, questions)
    items_limit = request.args.get('limit', 10, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1

    questions = \
              Question.query.filter(Question.category == str(category_id)).order_by(
                  Question.id
              ).limit(items_limit).offset(current_index * items_limit).all()
    paginated_questions = [question.format() for question in questions]
    if questions:
      return jsonify({
          'success': True,
          'status': 200,
          'questions': paginated_questions,
          'total_questions': len(paginated_questions)
      })
    else:
      return abort(400)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route("/quizzes", methods=['POST'])
  def get_nextquestion():
    if request.data:
      previous_questions = request.json.get('previous_questions')
      quiz_category = request.json.get('quiz_category')

      if not quiz_category:
          return abort(400)
      category_id = int(quiz_category.get('id'))  
      if (category_id == 0):
        nextquestions = Question.query.all()
      else:
        nextquestions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((previous_questions))).all()
          
      if nextquestions:
          return jsonify({
              "success": True,
              'status': 200,
              "question": Question.format(nextquestions[random.randrange(0,len(nextquestions))])
          })
      else:
       return abort(400)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

  @app.errorhandler(422)
  def unprocessable(error):
      return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

  @app.errorhandler(400)
  def bad_request(error):
      return (
            jsonify({"success": False, "error": 400, "message": "bad request"}), 
            400
        )
  
  return app

    