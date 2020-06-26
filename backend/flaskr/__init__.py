import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randint

from models import setup_db, Question, Category



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app,resources={r'*':{'origins':'*'}})


    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',"Content-Type, Authorizations,True")
      response.headers.add('Access-Control-Allow-Methods',"GET, POST, PATCH, DELETE, OPTIONS")
      return response

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
    # Pagination helper'
    questions_per_page = 10
    def pagination(request,selections):
      page = request.args.get('page',1,type=int)
      start = (page - 1) * questions_per_page
      end = start + questions_per_page
      items = [item.format() for item in selections]
      return items[start:end]

    # GET: /questions
    @app.route('/questions', methods=["GET"])
    def get_questions():
       all_questions = Question.query.order_by(Question.id).all()
       all_categories = Category.query.order_by(Category.id).all()
       paginate_questions = pagination(request,all_questions)
       categories = {category.id:category.type for category in all_categories}
       return jsonify({ "questions":paginate_questions,
       "total_questions":len(all_questions),"categories":categories , "current_category":None })

    # GET: /questions<question_id>
    @app.route('/questions/<int:question_id>', methods=["GET"])
    def get_questions_by_id(question_id):
       question = Question.query.filter_by(id=question_id).one_or_none()
       if question is None:
           abort(404)
       else:
           all_categories = Category.query.order_by(Category.id).all()
           # paginate_questions = pagination(request,all_questions)
           categories = {category.id:category.type for category in all_categories}

           return jsonify({ "questions":question.format(),
           "categories":categories , "current_category":None })
# "total_questions":len(question),
    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    # GET: /categories
    @app.route('/categories', methods=["GET"])
    def get_categoires():
        categories = Category.query.all()
        categories_list = {category.id:category.type for category in categories}
        return jsonify({"success": True, "categories":categories_list})


    '''
    @TODO: Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def delete_question(question_id):
        try:
            question_to_delete = Question.query.filter_by(id=question_id).one_or_none()
            if question_to_delete:
                question_to_delete.delete()
                return jsonify({"question_to_delete" :question_to_delete.format()})
            else:
              abort(404)
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
      body = request.get_json()
      new_question = body.get('question',None)
      new_category = body.get('category',None)
      new_difficulty = body.get('difficulty',None)
      new_answer = body.get('answer',None)
      try:
          question = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
          question.insert()
          return jsonify({'success':True, 'question': new_question, 'answer':new_answer,
          'difficulty':new_difficulty,'category':new_category})
      except :
          abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search_term',methods=['POST'])
    def get_questions_by_search_term():
        body = request.get_json()
        search_term = body.get('searchTerm',None)
        look_for = '%{0}%'.format(search_term)
        questions = Question.query.filter(Question.question.ilike(look_for)).all()
        if not questions:
            abort(404)
        else:
            questions_list = [question.format() for question in questions]
            total_questions = len(questions_list)
            current_category = Category.query.filter(Category.id==questions[0].category).one_or_none()
            return jsonify({"questions":questions_list,"totalQuestions":total_questions,
            "currentCategory":{current_category.id:current_category.type}})

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:categor_id>/questions',methods=['GET'])
    def get_question_by_category(categor_id):
        questions = Question.query.filter(Question.category==categor_id).all()
        category = Category.query.filter(Category.id==categor_id).one_or_none()
        if not questions:
            abort(404)
        else:
            questions_list = [question.format() for question in questions]
            total_questions = len(questions_list)
            return jsonify({"questions":questions_list,"totalQuestions":total_questions,
            "currentCategory":None})


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
    @app.route('/quizzes',methods=['POST'])
    def quizzes():
        header = request.get_json()
        previous_questions =  header.get('previous_questions')
        quiz_category =  header.get('quiz_category')
        #  case when ALL is clicked
        if quiz_category['id'] == 0:
            qusetions = Question.query.order_by(Question.id).all()
            category = Category.query.filter(Category.id==quiz_category['id']).all()
        else:
            qusetions = Question.query.filter(Question.category==quiz_category['id']).all()
            category = Category.query.filter(Category.id==quiz_category['id']).all()
        if not qusetions:
            abort(404)
        else:
            question_id = randint(0,len(qusetions)-1)
            while(question_id in previous_questions):
                question_id = randint(0,len(qusetions)-1)
                if question_id not in previous_questions:
                    break
            return jsonify({"question": qusetions[question_id].format()})

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def error_handler_404(error):
      return jsonify({"success":False, 'error':404, "message":"bad request, the resouse could not be found"})

    @app.errorhandler(422)
    def error_handerl_422(error):
        return jsonify({"succes":False,'error':422,"message":"bad request, unprocessable entity"})
    return app
