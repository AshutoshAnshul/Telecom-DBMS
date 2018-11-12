from flask import Flask,flash,redirect, render_template, request, url_for
import string
from random import *
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
						return redirect(url_for('showcustomer',id=username))
					elif username[0]=='S':
						return redirect(url_for('showkiosk',id=username))
					elif username[0]=='A':
						return redirect(url_for('admin',id=username))
					else :
						error='Invalid username. Please try again'
				else :
					error = 'Invalid password. Please try again!'
		else:
			error='Invalid username. Please try again'
	return render_template("login.html",error=error)

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
	if id=='A401':
		query=("select kiosk.*,contact,sim,landline,router from kiosk,kioskcontact,kioskstock where kiosk.kioskid=kioskcontact.kioskid and kiosk.kioskid=kioskstock.kioskid")
	else:
		query=("select kiosk.*,contact,sim,landline,router from kiosk,kioskcontact,kioskstock where kiosk.kioskid=kioskcontact.kioskid and kiosk.kioskid=kioskstock.kioskid and kiosk.kioskid in(Select kioskid from handles where employeeid='"+id+"');")
	cursor.execute(query)
	data= cursor.fetchall()
	print(data)
	return render_template("sales.html",name=id,data=data)

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


@app.route("/customer/<id>",methods=['GET','POST'])
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

	query=("Select * from customers")
	cursor.execute(query)
	data=cursor.fetchall()
	return render_template("customer.html",name=id,data=data,result=None,phone=None)


@app.route("/admin/<id>",methods=['GET','POST'])
def admin(id):
	if request.method=='POST':
		name=request.form['name']
		post=request.form['post']
		region=request.form['region']
		salary=request.form['salary']
		house=request.form['houseno']
		locality=request.form['locality']
		city=request.form['city']
		pin=request.form['pin']
		state=request.form['state']
		contact=request.form['contact']
		pan=request.form['pan']
		email=request.form['email']
	manage=None;add=None;
	query=("Select count(*) from customers")
	cursor.execute(query)
	result=cursor.fetchall()
	noc=result[0][0]
	query=("Select count(*) from employee")
	cursor.execute(query)
	result=cursor.fetchall()
	noe=result[0][0]
	query=("Select count(*) from kiosk")
	cursor.execute(query)
	result=cursor.fetchall()
	nok=result[0][0]
	query=("Select sum(cost) from customers,plan where customers.planid=plan.planid")
	cursor.execute(query)
	result=cursor.fetchall()
	rev=result[0][0]
	if request.form.get("navg","nothing")=='manage':
		manage="manage"
		print(manage)
	if request.form.get("navg","nothing")=='add':
		add="add"
		print(add)
	return render_template("admin.html",name=id,noc=noc,noe=noe,nok=nok,rev=rev,manage=manage,add=add)	

@app.route("/admin-manage/<id>",methods=['GET','POST'])
def manage(id):
	result=None;
	if request.method=='POST':
		if request.form.get("manage","nothing")=="Show":
			employeeid=request.form['empid']
			query=("Select * from employee where employeeid='"+employeeid+"'")
			cursor.execute(query)
			result=cursor.fetchall()
			print(result[0][1])
			return render_template("admin_manage.html",name=id,result=result,eid=employeeid)
		if request.form.get("update","nothing")=="Update":
			employeeid=request.form['empid']
			region=request.form['reg']
			salary=str(request.form['sal'])
			address=list(map(str,request.form['address'].split(",")))
			query=("Select * from employee where employeeid='"+employeeid+"'")
			cursor.execute(query)
			result=cursor.fetchall()
			if region==result[0][4] and salary==str(result[0][5]) and address[0]==str(result[0][6]) and address[1]==result[0][7] and address[2]==result[0][8] and address[3]==str(result[0][9]) and address[4]==result[0][10] :
				print("same")
			else:
				query=("update employee set region='"+region+"',salary='"+salary+"',house_no="+address[0]+",locality='"+address[1]+"',cityorvillage='"+address[2]+"',pincode="+address[3]+",state='"+address[4]+"' where employeeid='"+employeeid+"'")
				cursor.execute(query)
				connection.commit()
			query=("Select * from employee where employeeid='"+employeeid+"'")
			cursor.execute(query)
			result=cursor.fetchall()
			return render_template("admin_manage.html",name=id,result=result,eid=employeeid)
	return render_template("admin_manage.html",name=id,result=result)	

@app.route("/admin-add/<id>",methods=['GET','POST'])
def addemp(id):
	if request.method=='POST':
		name=request.form['name']
		post=request.form['post']
		region=request.form['reg']
		salary=request.form['sal']
		contacts=list(map(str,request.form['con'].split(",")))
		address=list(map(str,request.form['address'].split(",")))
		pan=request.form['pan']
		email=request.form['email']
		start=None
		if post=='Plan_Analyst':
		 start='P'
		elif post=='Sales_Manager':
		 start='S'
		elif post=='Customer_Manager':
		 start='C'
		last=None
		query=("select employeeid from employee where employeeid like '"+start+"%'")
		cursor.execute(query)
		res=cursor.fetchall()
		for r in res :
		  last=r[0]
		last=last[1:]
		lastint=int(last)+1
		employeeid=start+str(lastint)
		print(employeeid)
		query=("Insert into employee values('"+employeeid+"','"+name+"','"+post+"',curdate(),'"+region+"',"+salary+","+address[0]+",'"+address[1]+"','"+address[2]+"',"+address[3]+",'"+address[4]+"','"+pan+"','"+email+"')")
		cursor.execute(query)
		connection.commit()
		count=len(contacts)
		for i in range(count):
			query=("Insert into employeecontact values('"+employeeid+"',"+contacts[i]+")")
			cursor.execute(query)
			connection.commit()
		min_char = 8
		max_char = 12
		allchar = string.ascii_letters + string.punctuation + string.digits
		password = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
		print(password)
		query=("Insert into login values('"+employeeid+"','"+password+"')")
		cursor.execute(query)
		connection.commit()
	return render_template("admin_add.html",name=id)


if __name__ == '__main__':
	app.secret_key='super secret key'
	app.run(debug=True)
