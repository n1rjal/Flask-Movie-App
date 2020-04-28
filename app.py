from flask import Flask, escape, request, render_template,session,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from forsearch import searchreq
from datetime import timedelta
from hashlib import sha256
import requests

app = Flask(__name__)

#This is how much favourite movie data last
app.config["SESSION_PERMANENT"]=True
app.config["PERMANENT_SESSION_LIFETIME"]=timedelta(days=10)

#sha256(("this is aju's work").encode('utf-8')).hexdigest()
app.config["secret-key"]="87ce5b467a46f3702469ab7c9524fed8b8483a604530304ea2b84108b5af461b"
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///./backdata.db"

db=SQLAlchemy(app)

'''
##copy and run this code in python terminal
from hashlib import sha256
text=csaju.encode("utf-8")
text=sha256(text).hexdigest()
print(text)
#output is d273fd202ae36a79dd36f160616859903861e535d49b44793b1d2930b05ff33a
'''

#and encoded in hexadecimal
#for session
app.secret_key="d273fd202ae36a79dd36f160616859903861e535d49b44793b1d2930b05ff33a"

#DATABSE MODELS this is generally used as models.py in django

#for user table
class User(db.Model):
	__tablename__='user'
	_id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(20),unique=True)
	email=db.Column(db.String(100))
	password=db.Column(db.String(64))
	favliked=db.relationship('Movie',backref="user")

	def __repr__(self):
		return ("The data belongs to {}".format(self.username))

#for movie TABLE
class Movie(db.Model):
	__tablename__='movie'
	_id=db.Column(db.Integer,primary_key=True)
	moviename=db.Column(db.String(100))
	poster=db.Column(db.String(1000))
	movietype=db.Column(db.String(100))
	imdb=db.Column(db.String(1000))
	year=db.Column(db.String(4))
	user_id=db.Column(db.Integer,db.ForeignKey('user._id'))

	def __repr__(self):
		return ("the data is of {}".format(self.moviename))

#writing in database
def writeuser(username,email,password):
	validusername=True
	allusers=User.query.filter_by(username=username).all()
	for user in allusers:
		#user's username
		usersname=user.username
		if username==usersname:
			validusername=False
			
	#encrypting the password
	if validusername:
		password=password.encode("utf-8")
		password=sha256(password)
		password=password.hexdigest()
		
		sampleuser=User(username=username,email=email,password=password)
		db.session.add(sampleuser)
		db.session.commit()
		

		allusers=User.query.all()
		
		for user in allusers:
			if username==user.username:
				uid=user._id
				session['uid']=uid

	else:
		flash("Username already taken")
		return ("UAT")

	
@app.route("/signup",methods=["POST"])
def signuppost():
	if request.method=="POST":
		username=request.form["uname"]
		password=request.form["pwd"]
		email=request.form['email']
		resp=writeuser(username=username,email=email,password=password)
		if resp=="UAT":
			return redirect(url_for("signup"))
		else:
			return redirect(url_for("index"))


#writemovie
@app.route("/addtofav",methods=["POST"])
def writefavmovie():
	if loggedin():
		
		userid=session["uid"]

		moviename=request.form["title"]
		poster=request.form["poster"]
		movietype=request.form["type"]
		year=request.form["year"]
		imdb=request.form["imdb"]
		
		samplemovie=Movie(moviename=moviename,poster=poster,
				movietype=movietype,imdb=imdb,
				year=year,user_id=userid)

		db.session.add(samplemovie)
		db.session.commit()
		return ({"code":"sucess"})
	else:
		return ({"code":"signup"})


#methods for loggedin or not
def loggedin():
	try:
		username=session["uid"]
		return True
	except:
		return False


@app.route('/')
@app.route('/home')
def index():
	return render_template('index.html')

@app.route("/logout",methods=["GET"])
def logout():
	if loggedin():
		try:
			session.pop("uid")
			flash("Logged out sucessfully")
			return (redirect(url_for("index")))
		except:
			return (redirect(url_for("index")))
	else:
		return (redirect(url_for("index")))


@app.route("/login",methods=["POST","GET"])
def login():
	if request.method=="GET":
		if loggedin() is False:
			return render_template("login.html")
		else:
			return redirect(url_for("index"))
	
	if request.method=="POST":
		username=request.form["name"]
		
		password=request.form["pwd"]
		
		users=User.query.all()
		
		#now hashing the password 
		password=(sha256(password.encode("utf-8"))).hexdigest()
		for user in users:
			gotusername=user.username
			gotpassword=user.password
			gotemail=user.email
			if ((username==gotusername or username==gotemail )and password==gotpassword):
				session['uid']=user._id
				flash("Logged in Sucessfully")
				return redirect(url_for("index"))
		
		#in python there is for else too bro
		else:
			flash('PLease enter valid info')
			return redirect(url_for("login"))
		




@app.route("/signup",methods=["GET"])
def signup():
	if request.method=="GET":
		
		loggedstatus=loggedin()
		
		if loggedstatus is False:
			
			return (render_template("signin.html"))
		
		else:
			
			return (redirect(url_for("index")))
	


@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
	"""if POST, query movie api for data and return results."""
	title=request.form['title']
	try:
		jsonresp=searchreq(title)
		results=jsonresp["Search"]
		return render_template("search_results.html",results=results)
	except Exception as e:
		return render_template("notfound.html"),404


def getallfav():
	users=User.query.filter_by(index=session["uid"]).first()
	username=users.username
	favmovies=Movie.query.filter_by(user_id=users).all()
	return (favmovies)	


@app.route("/useraction")
def useraction():
	users=User.query.all()
	noofuser=0
	noofuser=User.query.order_by(User._id.desc()).first()
	noofuser=noofuser._id

	
	try:
		username=session["uid"]
		isloggedin=loggedin()
		user=User.query.filter_by(_id=username).first()
		username=user.username
		email=user.email
	except Exception as e:
		
		username=""
		email=""
		
		isloggedin=False
	return render_template("useraction.html",noofuser=noofuser,isloggedin=isloggedin,email=email,username=username)

@app.route('/favourites',methods=['GET'])
def favourite():
	if loggedin():
		if request.method=="GET":
			flash("Favourite movies last only for 31 days")
			uid=session["uid"]
			
			results=Movie.query.filter_by(user_id=uid).all()
			
			return (render_template("favourites.html",results=results))
		
	else:
		flash("Please login to see your content")
		return(redirect(url_for("useraction")))

@app.errorhandler(404)
def notfound(error):
	return render_template('notfound.html'),404



if __name__=="__main__":
	app.run(debug=True)
