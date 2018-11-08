from flask import Flask,flash,redirect, render_template, request, url_for
import mysql.connector
try:
	connection=mysql.connector.connect(user='root',password='12345',host='localhost',database='project')
	cursor=connection.cursor()
	print("connected")
except:
	print("not connected")

app= Flask(__name__)

@app.route("/")
@app.route("/login",methods=['GET','POST'])
def login():
	error=None
	if request.method== 'POST':
		username=request.form['usern']
		password=request.form['passw']
		print(username)
		print(password)
		query=("Select password from login where username='"+username+"';")
		print(query)
		cursor.execute(query)
		result= cursor.fetchall()
		tot=len(result)
		if tot>0 :
			for r in result:
				if password==r[0]:
					if username[0]=='P':
						return redirect(url_for('showplan',id=username))	
					elif username[0]=='C':
						return render_template("customer.html",name=username,data=None,result=None,phone=None)
					elif username[0]=='S':
						return redirect(url_for('showkiosk',id=username))
					else :
						error='Invalid username. Please try again'
				else :
					error = 'Invalid password. Please try again!'
		else:
			error='Invalid username. Please try again'
	return render_template("login.html",error=error)


@app.route("/plan",methods=['GET','POST'])
@app.route("/plan/<id>",methods=['GET','POST'])
def showplan(id):
	if request.method=='POST':
		planid=request.form['planid']
		query=("Select * from plan where Planid='"+planid+"';")
		print(query)
		cursor.execute(query)
		result=cursor.fetchall()
		tot=len(result)
		if tot>0:
			return render_template("planedit.html",name=id,result=result)
	else :
		query=("Select * from plan")
		cursor.execute(query)
		data= cursor.fetchall()
		return render_template("plan.html",name=id,data=data)

@app.route("/planadded",methods=['POST'])
@app.route("/planadded/<id>",methods=['POST'])
def add(id):
	if request.method=='POST':
		planid=request.form['planid']
		planname=request.form['planname']
		cost=request.form['cost']
		validity=request.form['validity']
		talktime=request.form['talktime']
		sms=request.form['sms']
		data=request.form['data']
		query=("Insert into plan values('"+planid+"','"+planname+"',"+cost+","+validity+","+talktime+","+sms+","+data+");")
		cursor.execute(query)
		connection.commit()
		query=("Select employeeid,kioskid from employee,kiosk where employee.region=kiosk.region and employee.post='sales_manager'")
		cursor.execute(query)
		result=cursor.fetchall()
		for r in result:
			query=("Insert into handles values('"+r[0]+"','"+r[1]+"');")
			cursor.execute(query)
			connection.commit()
		return redirect(url_for('showplan',id=id))

@app.route("/planedit",methods=['POST'])
@app.route("/planedit/<id>",methods=['POST'])
def editplan(id):
	if request.method=='POST':
		planid=request.form["plan_id"]
		cost=request.form["cost"]
		validity=request.form["validity"]
		talktime=request.form["talktime"]
		sms=request.form["sms"]
		data=request.form["data"]
		if request.form["change"]=='Change details' :
			query=("Update plan set cost="+cost+",validity="+validity+",talktime="+talktime+",sms_per_day="+sms+",data="+data+" where planid='"+planid+"';")
			cursor.execute(query)
			connection.commit()
		elif request.form["change"]=='Delete this Plan' :
			query=("Delete from plan where planid='"+planid+"';")
			cursor.execute(query)
			connection.commit()
		return redirect(url_for('showplan',id=id))

@app.route("/sales",methods=['GET','POST'])
@app.route("/sales/<id>",methods=['GET','POST'])
def showkiosk(id):
	if request.method=='POST':
		kioskid=request.form["kioskid"]
		if request.form["coa"]=="Change Contact_no" :
			query=("Select contact from kioskcontact where kioskid='"+kioskid+"';")
			cursor.execute(query)
			result=cursor.fetchall()
			return render_template("salesedit.html",name=id,data=result,kioskid=kioskid)
		elif request.form["coa"]=="Update" :
			sim=request.form['sim']
			landline=request.form['landline']
			router=request.form['router']
			query=("Update kioskstock set sim=sim+"+sim+",landline=landline+"+landline+",router=router+"+router+" where kioskid='"+kioskid+"'")
			cursor.execute(query)
			connection.commit()
			return redirect(url_for('showkiosk',id=id))
	query=("select kiosk.*,contact,sim,landline,router from kiosk,kioskcontact,kioskstock where kiosk.kioskid=kioskcontact.kioskid and kiosk.kioskid=kioskstock.kioskid and kiosk.kioskid in(Select kioskid from handles where employeeid='"+id+"');")
	cursor.execute(query)
	data= cursor.fetchall()
	print(data)
	return render_template("sales.html",name=id,data=data)

@app.route("/kioskchange",methods=['POST'])
@app.route("/kioskchange/<id>",methods=['POST'])
def kioskchange(id):
	if request.method=='POST':
		kioskid=request.form["kioskid"]
		oldcontact=str(request.form.get('oldcontact'))
		newcontact=request.form["newcontact"]
		print(oldcontact)
		print(newcontact)
		print(id)
		query=("update kioskcontact set contact="+newcontact+" where contact="+oldcontact+" and kioskid='"+kioskid+"';")
		cursor.execute(query)
		connection.commit()
		return redirect(url_for('showkiosk',id=id))


@app.route("/customer",methods=['POST'])
@app.route("/customer/<id>",methods=['POST'])
def showcustomer(id):
	if request.method=='POST':
		phone=request.form["phone"]
		query=("Select * from customers where phone_no='"+phone+"'")
		cursor.execute(query)
		data=cursor.fetchall()
		result=None
		if request.form.get("dec","nothing")=='Deactivate/Activate':
			for item in data :
				if item[14]=='Activated':
					query=("Update customers set status='Deactivated' where phone_no='"+phone+"'")
				elif item[14]=='Deactivated':
					query=("Update customers set status='Activated' where phone_no='"+phone+"'")
			cursor.execute(query)
			connection.commit()

		elif request.form.get("dec","nothing")=='Change Plan':
			query=("Select planid from plan")
			cursor.execute(query)
			result=cursor.fetchall()

		if request.form.get("new plan","nothing")=='Change':
			plan=str(request.form.get('plan'))
			query1=("Select validity from plan where planid='"+plan+"'")
			cursor.execute(query1)
			validity=cursor.fetchall()
			day=validity[0][0]
			query=("Update customers set planid='"+plan+"',start_date=curdate(),end_date=date(date_add(start_date,interval "+str(day)+" day)) where phone_no='"+phone+"'")
			print(query)
			cursor.execute(query)
			connection.commit()
		query=("Select * from customers where phone_no='"+phone+"'")
		cursor.execute(query)
		data=cursor.fetchall()
		return render_template("customer.html",name=id,data=data,result=result,phone=phone)




if __name__ == '__main__':
	app.secret_key='super secret key'
	app.run(debug=True)
