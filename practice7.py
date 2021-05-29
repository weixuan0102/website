from flask import Flask, redirect , url_for, render_template, request, session, flash, jsonify, make_response
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

import json
app=Flask(__name__)
app.config['SECRET_KEY']='asdwd dawd8519'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

#model
class users(db.Model):
	id=db.Column("id",db.Integer,primary_key=True) #####
	name=db.Column(db.String(100))
	email=db.Column(db.String(100))

	def __init__(self, name,email):
		self.name=name
		self.email=email


@app.route("/")
def home():
	return render_template("index.html")

@app.route("/view")
def view():
	return render_template("view.html",values=users.query.all()) #users.query.all(): loop all the value in the database


@app.route("/login",methods=['POST','GET'])
def login():
	if request.method=='POST':
		session.permanent = True
		user=request.form["nm"] #request.form 是dictionary
		session["user"]=user
		found_user=users.query.filter_by(name=user).first()
		if found_user:
			session["email"]=found_user.email
		else:
			usr=users(user,"")
			db.session.add(usr)
			db.session.commit()

		flash("Login successful")
		return redirect(url_for("user"))
	else:
		if "user" in session:
			flash("already logged in")

			return redirect(url_for("user"))
		
		return render_template("login.html")

@app.route("/user",methods=["POST","GET"])
def user():
	email=None
	if "user" in session:
		user=session["user"]
		if request.method=="POST":
			email=request.form["email"]
			session["email"]=email
			found_user=users.query.filter_by(name=user).first()
			found_user.email=email
			db.session.commit()
			flash("Email was saved!")
		else:
			if "email" in session:
				email=session["email"]
		user=session["user"]
		found_user=users.query.filter_by(name=user).first()
		return render_template("user.html",email=email,user=found_user)
	else:
		flash("You are not logged in!")
		return redirect(url_for("login"))

@app.route("/delete_account",methods=['POST'])
def delete_account():
	user=json.loads(request.data)
	account_id=user['account_id']
	target=users.query.get(account_id)
	if target:
		db.session.delete(target)
		db.session.commit()
		flash("You deleted your account")

		session.pop("user",None) #####
		session.pop("email",None) #####
	return make_response('', 200) #####

	#return jsonify({})  #####
	
	
	#found_user=users.query.filter_by(name=user).all()
	#if found_user :
		#for user in found_user:
		#	user.delete()
		#	db.session.commit()
	
		


@app.route("/logout")
def logout():
	if "user" in session:
		user=session["user"]
		session.pop("user",None)
		session.pop("email",None)
		flash(f"You have been logged out,{user}","info")
	return redirect(url_for("login"))

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True)
