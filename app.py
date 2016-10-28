from flask import Flask, render_template, json, request, redirect, session, url_for
from flaskext.mysql import MySQL
from datetime import datetime, timedelta


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'cs2102'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



#navBar = ["home", "search", "admin", "user", "signup", "login",  "logout"]
#titleBar = ["Home", "Search", "Admin", "User", "Sign Up", "Login",  "Logout"]


def getSession():
	try:
		session['user'] = session.get('user')
		session['privilege'] = session.get('privilege')
	except KeyError:
		session['user'] = None
		session['privilege'] = None
	finally:
		if session.get('user') is None:
			navBar = ["home", "search", "signup", "login"]
			titleBar = ["Home", "Search", "Sign Up", "Login"]
		elif session.get('privilege') == 1:
			navBar = ["home", "search", "admin", "logout"]
			titleBar = ["Home", "Search", "Admin", "Logout"]
		else:
			user = session.get('user')
			navBar = ["home", "search", "user", "logout"]
			titleBar = ["Home", "Search", user.title(), "Logout"]

		return zip(navBar, titleBar)


@app.route('/')
@app.route('/home')
def main():
	
	navTitleBar = getSession()

	con = mysql.connect()
	cursor = con.cursor()

	try:
		
		
		#cursor.callproc('proc', (_username,_email, _password))
		sqlString = "SELECT * FROM Project"
		cursor.execute(sqlString)
		data = cursor.fetchall()

		endDateArr = []

		for i in range(0, len(data)):
			startDate = data[i][3]
			endDate = startDate + timedelta(days=int(data[i][4]))
			endDateArr.append(endDate)
		
		if len(data) > 0:
			con.commit()
			return render_template("index.html", navTitleBar=navTitleBar, page="home", projectData=zip(data, endDateArr))
			#return json.dumps({'message':'User created successfully !'})
		else:
			return render_template("index1.html")
			#return json.dumps({'error':str(data[0])})
		
	except Exception as e:
		#return json.dumps({'error':str(e)})
		return render_template("index2.html")
	finally:
		cursor.close() 
		con.close()



@app.route('/search', methods=['POST', 'GET'])
def search():
	navTitleBar = getSession()


	con = mysql.connect()
	cursor = con.cursor()

	try:		
		#cursor.callproc('proc', (_username,_email, _password))
		_mainSearch = request.form['mainSearch']
		#_keyword = request.form['keyword']
		#_owner = request.form['owner']
		#_amount = request.form['amount']
		
		sqlString = "SELECT * FROM Project WHERE title LIKE %s OR description LIKE %s", ('%' + _mainSearch + '%', '%' + _mainSearch + '%')
		cursor.execute(*sqlString)
		data = cursor.fetchall()

		endDateArr = []

		for i in range(0, len(data)):
			startDate = data[i][3]
			endDate = startDate + timedelta(days=int(data[i][4]))
			endDateArr.append(endDate)
		
		if len(data) > 0:
			con.commit()
			return render_template("search.html", navTitleBar=navTitleBar, page="search", projectData=zip(data, endDateArr), hide="")
			#return json.dumps({'message':'User created successfully !'})
		else:
			return render_template('search.html', navTitleBar=navTitleBar, page="search", hide="hidden", msg="No  Results")
			return json.dumps({'error':str(data[0])})
		
		#return render_template('search.html', navTitleBar=navTitleBar, page="search", hide="")
	except Exception as e:
		#return json.dumps({'error1':str(e)})
		return render_template('search.html', navTitleBar=navTitleBar, page="search", hide="hidden")
		#return render_template('search.html', navTitleBar=navTitleBar, page="search", hidden=hidden)
	finally:
		cursor.close() 
		con.close()

	#return render_template('search.html', navTitleBar=navTitleBar, page="search", hidden=hidden)


@app.route('/admin')
def admin():
	navTitleBar = getSession()
	if session.get('privilege') == 1:
		con = mysql.connect()
		cursor = con.cursor()

		try:		
			#cursor.callproc('proc', (_username,_email, _password))
			sqlString = "SELECT * FROM Project"
			cursor.execute(sqlString)
			data = cursor.fetchall()

			endDateArr = []

			for i in range(0, len(data)):
				startDate = data[i][3]
				endDate = startDate + timedelta(days=int(data[i][4]))
				endDateArr.append(endDate)
			
			if len(data) > 0:
				con.commit()
				return render_template("admin.html", navTitleBar=navTitleBar, page="admin", projectData=zip(data, endDateArr))
				#return json.dumps({'message':'User created successfully !'})
			else:
				return render_template("index1.html")
				#return json.dumps({'error':str(data[0])})
			
		except Exception as e:
			#return json.dumps({'error':str(e)})
			return render_template("index2.html")
		finally:
			cursor.close() 
			con.close()
	
	else:
		return render_template('error.html', navTitleBar=navTitleBar, page="admin", error="401 Unauthorized Access")

@app.route('/user')
def user():
	navTitleBar = getSession()
	con = mysql.connect()
	cursor = con.cursor()
	currDate = datetime.now().strftime('%Y-%m-%d')

	if session.get('privilege') == 1:
		return redirect("/admin")

	elif session.get('user') != None:
		try:
			_username = session.get('user')
			
			
			sqlString = "select * from Account where username = %s",  (_username)
			cursor.execute(*sqlString)

			data = cursor.fetchall()

			if len(data) > 0:

				sqlStringData = "select * from Project where creator = %s",  (_username)
				cursor.execute(*sqlStringData)

				projectData = cursor.fetchall()
				
				endDateArr = []
				for i in range(0, len(projectData)):
					startDate = projectData[i][3]
					endDate = startDate + timedelta(days=int(projectData[i][4]))
					endDateArr.append(endDate)
				
				# _hashed_password = generate_password_hash(_password)
				return render_template('user.html', navTitleBar=navTitleBar, page="user", project=zip(projectData, endDateArr), currDate=currDate)
			else:
				return json.dumps({'error':str(data[0])})

		except Exception as e:
			navTitleBar = getSession()
			return render_template('login.html', navTitleBar=navTitleBar, page="login", msg="Invalid Username/Password")

		finally:
			cursor.close()
			con.close()

		
	else:
		return render_template('error.html', navTitleBar=navTitleBar, page="user", error="401 Unauthorized Access")

@app.route('/delete')
def delete():
	_projectID= request.args.get('project')

	con = mysql.connect()
	cursor = con.cursor()

	try:
		_creator = session.get('user')
		_admin = session.get('privilege')
		htmlPage = "/user"
		
		if _admin != 1:
		#cursor.callproc('proc', (_username,_email, _password))
			sqlString = "DELETE FROM Project WHERE id=%s AND creator=%s", (_projectID, _creator)
		else:
			sqlString = "DELETE FROM Project WHERE id=%s", (_projectID)
			htmlPage = "/admin"

		cursor.execute(*sqlString)
		data = cursor.fetchall()

		if len(data) is 0:
			con.commit()
			return redirect(htmlPage)
			#return json.dumps({'message':'User created successfully !'})
		else:
			return redirect("/deleteElse")
			#return json.dumps({'error':str(data[0])})
		
	except Exception as e:
		#return json.dumps({'error':str(e)})
		return redirect("/deleteError")
	finally:
		cursor.close() 
		con.close()

@app.route('/edit')
def edit():
	navTitleBar = getSession()
	_projectID = request.args.get('project')
	
	
	con = mysql.connect()
	cursor = con.cursor()

	currDate = datetime.now().strftime('%Y-%m-%d')

	try:
		_creator = session.get('user')
		_admin = session.get('privilege')
		
		if _admin != 1:
			#cursor.callproc('proc', (_username,_email, _password))
			sqlString = "SELECT * FROM Project WHERE id=%s AND creator=%s", (_projectID, _creator)
		else:
			sqlString = "SELECT * FROM Project WHERE id=%s", (_projectID)

		cursor.execute(*sqlString)
		data = cursor.fetchall()

		if len(data) > 0:
			con.commit()
			return render_template("edit.html", navTitleBar=navTitleBar, page="user", data=data[0], currDate=currDate)
			#return json.dumps({'message':'User created successfully !'})
		else:
			return redirect("/edit1")
			#return json.dumps({'error':str(data[0])})
		

	except Exception as e:
		#return json.dumps({'error':str(e)})
		return redirect("/edit2")
	finally:
		cursor.close() 
		con.close()

@app.route('/editProject', methods=['POST', 'GET'])
def editProject():
	navTitleBar = getSession()
	
	
	con = mysql.connect()
	cursor = con.cursor()

	try:
		_projectID= request.form['projectID']
		_title = request.form['title']
		_description = request.form['description']
		_startDate = request.form['startDate']
		_duration = request.form['duration']
		_amount = request.form['amount']
		_creator = session.get('user')
		_admin = session.get('privilege')
		
		if _admin != 1:
			#cursor.callproc('proc', (_username,_email, _password))
			sqlString = "UPDATE Project SET title=%s, description=%s, startDate=%s, duration=%s, fundtarget=%s \
						WHERE id=%s AND creator=%s", (_title, _description, _startDate, _duration, _amount, _projectID, _creator)
		else:
			sqlString = "UPDATE Project SET title=%s, description=%s, startDate=%s, duration=%s, fundtarget=%s \
						WHERE id=%s", (_title, _description, _startDate, _duration, _amount, _projectID)

		cursor.execute(*sqlString)
		data = cursor.fetchall()

		if len(data) is 0:
			con.commit()
			return redirect(url_for('user',msg='success'))
			#return json.dumps({'message':'User created successfully !'})
		else:
			return redirect(url_for('user',msg=str(data[0])))
			#return json.dumps({'error':str(data[0])})
		
		
	except Exception as e:
		#return json.dumps({'error':str(e)})
		return redirect(url_for('user',msg=str(e)))
	finally:
		cursor.close() 
		con.close()
	

@app.route('/signup')
def signup():
	navTitleBar = getSession()
	
	msg = request.args.get('msg')
	alert = "warning"

	if msg  == 'success':
		msg = "Account successfully created"
		alert = "success"
	elif msg == None:
		msg = ""
	elif msg == 'password':
		msg = "Password do not match"
	else:
		msg = "Username '" + msg.title()   + "' has been taken. Please choose another username" 
	

	return render_template('signup.html', navTitleBar=navTitleBar, page="signup", msg=msg, alert=alert)

@app.route('/validateSignup', methods=['POST', 'GET'])
def validateSignup():
	navTitleBar = getSession()
	
	
	con = mysql.connect()
	cursor = con.cursor()

	try:
		
		_username = request.form['username']
		_email = request.form['email']
		_pass1 = request.form['password1']
		_pass2 = request.form['password2']

		if _pass1 != _pass2:
			return redirect(url_for('signup',msg='password'))
		
		_password = _pass1
		#cursor.callproc('proc', (_username,_email, _password))
		sqlString = "INSERT INTO account(username, email, password) VALUES(%s, %s, %s)", (_username, _email, _password)
		cursor.execute(*sqlString)
		data = cursor.fetchall()

		if len(data) is 0:
			con.commit()
			return redirect(url_for('signup',msg='success'))
			#return json.dumps({'message':'User created successfully !'})
		else:
			return redirect(url_for('signup',msg=_username))
			#return json.dumps({'error':str(data[0])})
		
	except Exception as e:
		#return json.dumps({'error':str(e)})
		return redirect(url_for('signup',msg=_username))
	finally:
		cursor.close() 
		con.close()
		
	
	
@app.route('/login')
def login():
	navTitleBar = getSession()
	return render_template('login.html', navTitleBar=navTitleBar, page="login")

@app.route('/validateLogin',methods=['POST'])
def validateLogin():

	con = mysql.connect()
	cursor = con.cursor()

	try:
		_username = request.form['username']
		_password = request.form['password']

		con = mysql.connect()
		cursor = con.cursor()
		sqlString = "select * from Account where username = %s",  (_username)
		cursor.execute(*sqlString)

		data = cursor.fetchall()

		if len(data) > 0:
			# _hashed_password = generate_password_hash(_password)
			if str(data[0][2]) == str(_password):
				session['user'] = data[0][0]
				session['privilege'] = data[0][3]
				if session.get('privilege') == 1:
					return redirect('/admin')
				else:
					return redirect('/user')
			else:
				return render_template('login.html', navTitleBar=navTitleBar, page="login", msg="Invalid Username/Password")
		else:
			return json.dumps({'error':str(data[0])})

	except Exception as e:
		navTitleBar = getSession()
		return render_template('login.html', navTitleBar=navTitleBar, page="login", msg="Invalid Username/Password")

	finally:
		cursor.close()
		con.close()

@app.route('/logout')
def logout():
	session.pop('user',None)
	session.pop('privilege',None)
	return redirect('/')


@app.route('/createProject',methods=['POST', 'GET'])
def createProject():
	navTitleBar = getSession()
	
	
	con = mysql.connect()
	cursor = con.cursor()

	try:
		
		_title = request.form['title']
		_description = request.form['description']
		_startDate = request.form['startDate']
		_duration = request.form['duration']
		_amount = request.form['amount']
		_creator = session.get('user')
		
		#cursor.callproc('proc', (_username,_email, _password))
		sqlString = "INSERT INTO project(title, description, startDate, duration, fundtarget, creator) \
					VALUES(%s, %s, %s, %s, %s, %s)", (_title, _description, _startDate, _duration, _amount, _creator)
		cursor.execute(*sqlString)
		data = cursor.fetchall()

		if len(data) is 0:
			con.commit()
			return redirect(url_for('user',msg='success'))
			#return json.dumps({'message':'User created successfully !'})
		else:
			return redirect(url_for('user',msg=str(data[0])))
			#return json.dumps({'error':str(data[0])})
		
	except Exception as e:
		#return json.dumps({'error':str(e)})
		return redirect(url_for('user',msg=str(e)))
	finally:
		cursor.close() 
		con.close()

@app.route('/view')
def view():
	navTitleBar = getSession()

	_projectID = request.args.get('project')
	_user = session.get('user')

	con = mysql.connect()
	cursor = con.cursor()

	currDate = datetime.now().strftime('%Y-%m-%d')

	try:
		sqlString = "SELECT * FROM Project WHERE id=%s", (_projectID)

		cursor.execute(*sqlString)
		data = cursor.fetchall()

		endDateArr = []

		for i in range(0, len(data)):
			startDate = data[i][3]
			endDate = startDate + timedelta(days=int(data[i][4]))
			endDateArr.append(endDate)

		if len(data) > 0:
			con.commit()
			return render_template('view.html',navTitleBar=navTitleBar, page="home", projectID=_projectID, projectData=data[0], endDate=endDate, user=_user)
			#return json.dumps({'message':'User created successfully !'})
		else:
			return render_template('view.html',navTitleBar=navTitleBar, page="home", projectID=_projectID)
			#return json.dumps({'error':str(data[0])})
		

	except Exception as e:
		#return json.dumps({'error':str(e)})
		return render_template('view.html',navTitleBar=navTitleBar, page="home", projectID=_projectID)
	finally:
		cursor.close() 
		con.close()

@app.route('/contribute',methods=['POST', 'GET'])
def contribute():
	_projectID = request.args.get('project')
	_userID = request.args.get('user')
	return redirect('/view?project=' + _projectID + _userID)


if __name__ == "__main__":
	app.run()