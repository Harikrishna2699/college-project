from flask import Flask,render_template,request,redirect,session
from sklearn.ensemble import RandomForestClassifier
import pickle


import smtplib
server=smtplib.SMTP("smtp.gmail.com",587)
server.starttls()
server.login("sepsishospital2020@gmail.com","qwerty@123")

import sqlite3
con=sqlite3.connect('sepdb.db')
cur=con.cursor()
cur.execute('create table if not exists userdata(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,email TEXT NOT NULL, phnumber TEXT NOT NULL,username TEXTNOT NULL, password TEXT NOT NULL)')
cur.execute('create table if not exists result(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,username TEXTNOT NULL,email TEXT NOT NULL, phnumber TEXT NOT NULL,result TEXT NOT NULL)')
cur.execute('create table if not exists result1(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,username TEXTNOT NULL,email TEXT NOT NULL, phnumber TEXT NOT NULL,result TEXT NOT NULL)')
cur.execute('create table if not exists result2(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,username TEXTNOT NULL,email TEXT NOT NULL, phnumber TEXT NOT NULL,result TEXT NOT NULL)')

app=Flask(__name__)
app.secret_key='abc'

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/register',methods=['POST','GET'])
def savereg():
    if request.method=='POST':
        uemail=request.form['1']
        mobno=request.form['2']
        uname1=request.form['3']
        pass1=request.form['4']
        cnpass=request.form['5']
        if pass1==cnpass:
            with sqlite3.connect('sepdb.db') as con:
                cur=con.cursor()
                cur.execute('insert into userdata(email,phnumber,username,password) values(?,?,?,?)',(uemail,mobno,uname1,pass1))
                con.commit()
                return redirect('login')
        else:
            return redirect('/')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login',methods=['POST','GET'])
def savelog():
    if request.method == "POST":
        username=request.form['1']
        password=request.form['2']
        with sqlite3.connect("sepdb.db") as con:
            cur = con.cursor()
            cur.execute("select * from userdata where username=?",(username,))
            rows = cur.fetchone()

            u1=rows[3]
            u2=rows[4]

            if((username ==u1 ) and (password == u2)):
                session['email']=rows[1]
                session['username']=rows[3]
                session['phnumber']=rows[2]
                return render_template('Predict_sepsis.html')
            else:
                return render_template('login.html')
        return render_template('Predict_sepsis.html')

@app.route('/predict_sepsis',methods=['POST','GET'])
def sepsis():
    if request.method=="POST":
        model=pickle.load(open('test1.pickle','rb'))
        d={"Yes":0,"No":1,"yes":0,"no":1,"YES":0,"NO":1}
        Loc=request.form['Loc']
        Res=float(request.form['Res'])
        Hr=float(request.form['Hr'])
        Wbc=float(request.form['Wbc'])
        Temp=float(request.form['Temp'])
        Con=request.form['Con']
        Con=d[Con]
        Crp=float(request.form['Crp'])
        print(Crp,Loc,Res)
        s=model.predict([[Res,Hr,Wbc,Temp,Con,Crp]])
        if s[0]==0:
            return render_template('notpredict.html')
        else:
            a='sepsis symptoms'
            a1="email={0}\n username={1} \n phnumber={3} \n result={2}".format(session['email'],session['username'],a,session['phnumber'])
            con=sqlite3.connect('sepdb.db')
            cur=con.cursor()
            cur.execute('insert into result(username,email,phnumber,result)values(?,?,?,?)',(session['username'],session['email'],session['phnumber'],a))
            con.commit()
            server.sendmail("sepsishospital2020@gmail.com","aj97899791@gmail.com",a1)
            return redirect('/predict_severe')
    return render_template('Predict_sepsis.html')

@app.route('/predict_severe',methods=['POST','GET'])
def severe():
    if request.method=='POST':
        model=pickle.load(open('test2.pickle','rb'))
        un=float(request.form['Un'])
        sp=float(request.form['SP'])
        print(un,sp)
        s=model.predict([[un,sp]])
        print(s)
        if s[0]==2:
            a='seviour sepsis'
            a1="email={0}\n username={1} \n phnumber={3} \n result={2}".format(session['email'],session['username'],a,session['phnumber'])
            con=sqlite3.connect('sepdb.db')
            cur=con.cursor()
            cur.execute('insert into result1(username,email,phnumber,result)values(?,?,?,?)',(session['username'],session['email'],session['phnumber'],a))
            con.commit()
            server.sendmail("sepsishospital2020@gmail.com","aj97899791@gmail",a1)
            return redirect('/predict_shock')
        else:
            return render_template('notsevere.html')
    return render_template('Predict_severe.html')

@app.route('/predict_shock',methods=['POST','GET'])
def shock():
    if request.method=='POST':
        model=pickle.load(open('test3.pickle','rb'))
        bp=float(request.form['BpS'])
        bd=float(request.form['BpD'])
        un=float(request.form['Un'])
        gl=float(request.form['Gl'])
        cr=float(request.form['Cr'])
        lc=float(request.form['Lc'])
        bl=float(request.form['Bl'])
        inr=float(request.form['Inr'])
        pl=float(request.form['PL'])
        s=model.predict([[bp,bd,un,gl,cr,lc,bl,inr,pl]])
        print(s)
        if s[0]==3:
            a='septic shock'
            a1="email={0}\n username={1} \n phnumber={3} \n result={2}".format(session['email'],session['username'],a,session['phnumber'])
            con=sqlite3.connect('sepdb.db')
            cur=con.cursor()
            cur.execute('insert into result2(username,email,phnumber,result)values(?,?,?,?)',(session['username'],session['email'],session['phnumber'],a))
            con.commit()           
            server.sendmail("sepsishospital2020@gmail.com","aj97899791@gmail",a1)
            return render_template('hospital.html')
             
        else:
            return render_template('notshock.html')
            
    return render_template('Predict_shock.html')

@app.route('/hospital')
def sep():
    return render_template('hospital.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__ == "__main__":
    app.run(debug=True)
