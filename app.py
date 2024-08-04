from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

conn = mysql.connector.connect(host="localhost",username="root",password="Mp!2005",database="perfume_company")
cursor = conn.cursor()
@app.route('/')
def index():
   return render_template('index.html')

@app.route('/Registration',methods=['POST','GET'])
def Registration():
   if request.method == 'POST':
      username = request.form.get('username')
      password = request.form.get('password')
      confirm_password = request.form.get('confirm_password')
      email = request.form.get('email')
      gender = request.form.get('Gender')
      country = request.form.get('country')
      if not username or not password or not email or not gender or not country:
         return "All feilds are required",400
      if password != confirm_password:
         return "password doesn't match",400

      register(username,password,email,gender,country)
      return redirect(url_for('index'))
   return render_template('Registration.html')

@app.route('/login',methods=['POST','GET'])
def login():
   if request.method=='POST':
      username = request.form.get('username')
      password = request.form.get('password')
      cursor.execute("SELECT password FROM customerdetails WHERE username=%s", (username,))
      result = cursor.fetchone()

      if result and check_password_hash(result[0], password):
         return redirect(url_for('index'))
      else:
         return 'Invalid username',400
   return render_template('login.html')

def register(username,password,email,gender,country):
   hashed_password = generate_password_hash(password)
   query = "INSERT INTO customerdetails(username,password,email,gender,country) VALUES(%s,%s,%s,%s,%s)"
   values = (username,hashed_password,email,gender,country)
   cursor.execute(query,values)
   conn.commit()

if __name__ == '__main__':
   app.run(debug=True)

