from application import app, db, api
from flask import render_template, request, json, Response, redirect, flash, url_for, session, jsonify
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm

from flask_restplus import Resource

############################################################

# via localhost:5000/v1/api
@api.route('/api','/api/')
class GetAndPost(Resource):
	''' Get All '''
	def get(self):
		return jsonify(User.objects.all())

	''' POST '''
	def post(self):
		data 		= api.payload
		user_id 	= data['user_id']
		email 		= data['email']
		first_name 	= data['first_name']
		last_name 	= data['last_name']
		password 	= data['password']

		user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
		user.set_password(password)
		user.save() 
		return jsonify(User.objects(user_id=user_id))

@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
	''' Get One '''
	def get(self, idx):
		return jsonify(User.objects(user_id=idx))

	''' Put '''
	def put(self, idx):
		data = api.payload 
		User.objects(user_id=idx).update(**data)

		return jsonify(User.objects(user_id=idx))

	''' Delete '''
	def delete(self, idx):
		data = api.payload
		User.objects(user_id=idx).delete()
		return jsonify('User deleted!')

############################################################

# coursesData = [
# 	{"courseID":"1111","title":"PHP 101","description":"Intro to PHP","credits":3,"term":"Fall, Spring"}, 
# 	{"courseID":"2222","title":"Java 1","description":"Intro to Java Programming","credits":4,"term":"Spring"}, 
# 	{"courseID":"3333","title":"Adv PHP 201","description":"Advanced PHP Programming","credits":3,"term":"Fall"}, 
# 	{"courseID":"4444","title":"Angular 1","description":"Intro to Angular","credits":3,"term":"Fall, Spring"}, 
# 	{"courseID":"5555","title":"Java 2","description":"Advanced Java Programming","credits":4,"term":"Fall"}
# ]

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
	return render_template('index.html', index=True)

@app.route('/courses')
@app.route('/courses/')
@app.route('/courses/<term>')
def courses(term=None):
	if term == None: 
		term = 'Spring 2019'

	# without aggregate
	classes = Course.objects.order_by("+courseID")

	# with aggregate (only show courses that have not enrolled in) -- change the r1.user_id 
	# classes = list(Course.objects.aggregate(*[
	# 		{
	# 			'$lookup': {
	# 				'from': 'enrollment', 
	# 				'localField': 'courseID', 
	# 				'foreignField': 'courseID', 
	# 				'as': 'r1'
	# 			}
	# 		}, {
	# 			'$match': {
	# 				'r1.user_id': {
	# 					'$nin': [
	# 						4
	# 					]
	# 				}
	# 			}
	# 		}, {
	# 			'$sort': {
	# 				'courseID': 1
	# 			}
	# 		}
	# 	]))

	return render_template('courses.html', coursesData=classes, courses=True, term=term)

@app.route('/register', methods=['GET','POST'])
def register():
	if session.get('first_name'):
		return redirect(url_for('index'))

	form = RegisterForm()

	if form.validate_on_submit():
		user_id = User.objects.count()
		user_id += 1

		email		= form.email.data 
		password 	= form.password.data
		first_name 	= form.first_name.data
		last_name 	= form.last_name.data 

		user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
		user.set_password(password)
		user.save() 
		flash("You're registered now!","success")
		return redirect(url_for('index'))

	return render_template('register.html', register=True, form=form)

@app.route('/login', methods=['GET','POST'])
def login():
	if session.get('first_name'):
		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():
		email 	 = form.email.data
		password = form.password.data

		user = User.objects(email=email).first()

		if user and user.get_password(password):
			# if success
			flash(f"{user.first_name}, you're successfully login!", "success")
			session['user_id'] = user.user_id
			session['first_name'] = user.first_name
			return redirect(url_for('index'))
		else:
			# if not success
			flash("Sorry incorrrect email/password", "danger")
	return render_template('login.html', login=True, form=form, title="Login")

@app.route('/logout')
def logout():
	session['user_id'] = False
	session.pop('first_name', None)
	return redirect(url_for('index'))

@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():
	if not session.get('first_name'):
		return redirect(url_for('login'))
	
	courseID = request.form.get('courseID')
	courseTitle = request.form.get('title')
	user_id = session.get('user_id')

	if courseID:
		if Enrollment.objects(user_id=user_id, courseID=courseID):
			flash(f"You're already registered in this course { courseTitle }","danger")
			return redirect(url_for('courses'))
		else:
			enrollment = Enrollment(user_id=user_id, courseID=courseID)
			enrollment.save()
			flash(f"You're enrolled in { courseTitle }!","success")
	
	classes = list(User.objects.aggregate(*[
				{
					'$lookup': {
						'from': 'enrollment', 
						'localField': 'user_id', 
						'foreignField': 'user_id', 
						'as': 'r1'
					}
				}, {
					'$unwind': {
						'path': '$r1', 
						'includeArrayIndex': 'r1_id', 
						'preserveNullAndEmptyArrays': False
					}
				}, {
					'$lookup': {
						'from': 'course', 
						'localField': 'r1.courseID', 
						'foreignField': 'courseID', 
						'as': 'r2'
					}
				}, {
					'$unwind': {
						'path': '$r2', 
						'preserveNullAndEmptyArrays': False
					}
				}, {
					'$match': {
						'user_id': user_id
					}
				}, {
					'$sort': {
						'r2.courseID': 1
					}
				}
			]))

	# classes = list(Course.objects.aggregate(*[
	# 		{
	# 			'$lookup': {
	# 				'from': 'enrollment', 
	# 				'localField': 'courseID', 
	# 				'foreignField': 'courseID', 
	# 				'as': 'r1'
	# 			}
	# 		}, {
	# 			'$match': {
	# 				'r1.user_id': user_id
	# 			}
	# 		}
	# 	]))

	return render_template('enrollment.html', classes=classes, title="Enrollment", enrollment=True)

# @app.route('/api')
# @app.route('/api/')
# @app.route('/api/<idx>')
# def api(idx=None):
# 	if idx == None:
# 		jsonData = coursesData
# 	else:
# 		jsonData = coursesData[int(idx)]

# 	return Response(json.dumps(jsonData), mimetype='application/json')	


@app.route('/user')
def user():
	# User(user_id=1, firstName='Chris',lastName='John', email='chrisjohn@gmail.com', password='chrisjohn123').save()
	# User(user_id=2, firstName='John',lastName='Doe', email='johndoe@gmail.com', password='johndoe123').save()

	users = User.objects.all()

	return render_template('user.html', users=users)

