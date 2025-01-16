from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from flask_mail import *
from werkzeug.security import generate_password_hash,check_password_hash
import os

app = Flask(__name__)
app.secret_key = "*****" #your password
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465     
app.config["MAIL_USERNAME"] = 'perfectperfumeteam@gmail.com'  
app.config['MAIL_PASSWORD'] = '*****' #your smtp password  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True
  
mail = Mail(app)

def get_db_connection():
    conn = mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_DBNAME']
    )
    return conn


@app.route('/',methods=['POST','GET'])
def index():
   return render_template('index.html')

@app.route('/Registration',methods=['POST','GET'])
def Registration():
   if request.method == 'POST':
      username = request.form.get('username')
      password = request.form.get('password')
      email = request.form.get('email')
      if not username or not password or not email:
         return "All fields are required!",400
      
      session['user_status'] = "Registered"
      session['username'] = username
      
      register(username,password,email)
      return redirect(url_for('index'))
   return render_template('Registration.html')

@app.route('/login',methods=['POST','GET'])
def login():
   if request.method=='POST':
      username = request.form.get('username')
      password = request.form.get('password')
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT password FROM customerdetails WHERE username=%s", (username,))
      result = cursor.fetchone()
      cursor = conn.cursor()
      conn.close()
      
      if result and check_password_hash(result[0], password):
         session['user_status'] = "logged_in"
         session['username'] = username
         return redirect(url_for('index'))
      else:
         return 'Invalid username',400
   return render_template('login.html')

def register(username,password,email):
   conn = get_db_connection()
   cursor = conn.cursor()
   hashed_password = generate_password_hash(password)
   query = "INSERT INTO customerdetails(username,password,email) VALUES(%s,%s,%s)"
   values = (username,hashed_password,email)
   cursor.execute(query,values)
   conn.commit()
   cursor.close()
   conn.close()

@app.route('/view_cart',methods=['GET'])
def view_cart():
   if 'user_status' in session and (session['user_status']=="Registered" or session['user_status']=="logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
      user_id = cursor.fetchone()
      if user_id:
         user_id = user_id[0]
         cursor.execute("""SELECT p.product_name,p.target_gender,p.item_form,p.Ingredients,p.special_feature,p.item_volume,p.country,c.quantity,(p.price*c.quantity) as price 
                        from cart c 
                        join product p on p.product_id = c.product_id 
                        where c.user_id = %s
                        order by c.added_time DESC""",(user_id,))
         cart_items = cursor.fetchall()
         total_price_cart=0
         for item in cart_items:
            total_price_cart += item[8] 
         cursor.close()
         conn.close()
         return render_template('cart.html',cart_items = cart_items, grand_total = total_price_cart)
   else:
      return redirect(url_for('login'))

@app.route('/myprofile',methods=['POST','GET'])
def myprofile():
      if 'user_status' in session and (session['user_status'] == 'Registered' or session['user_status'] == 'logged_in'):
         username = session.get('username') 
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute("SELECT * FROM customerdetails WHERE username=%s", (username,))
         user_details = cursor.fetchone()
         cursor.close()
         conn.close()
         if user_details:
            return render_template('myprofile.html',user=user_details)
         else:
            return "user not found",400
      else:
         return redirect(url_for('login'))
      

@app.route('/Floral',methods=['POST','GET'])
def Floral():
   return render_template('Floral.html')

@app.route('/Woody',methods=['POST','GET'])
def Woody():
   return render_template('Woody.html')

@app.route('/Citrus',methods=['POST','GET'])
def Citrus():
   return render_template('Citrus.html')

@app.route('/Oriental',methods=['POST','GET'])
def Oriental():
   return render_template('Oriental.html')

@app.route('/Fresh_Aquatic',methods=['POST','GET'])
def Fresh_Aquatic():
   return render_template('Fresh_Aquatic.html')

@app.route('/Gourmand',methods=['POST','GET'])
def Gourmand():
   return render_template('Gourmand.html')

@app.route('/home',methods=['POST','GET'])
def home():
   return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>',methods=['GET','POST'])
def add_to_cart(product_id):
   if 'user_status' in session and (session['user_status']=="Registered" or session['user_status']=="logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
      user_id = cursor.fetchone()
      if user_id:
         user_id = user_id[0]
         quantity = int(request.form.get('quantity',1))
         cursor.execute("SELECT quantity from cart where user_id = %s and product_id = %s",(user_id,product_id))
         product_exists = cursor.fetchone()
         if product_exists:
            new_quantity = product_exists[0] + quantity
            cursor.execute("UPDATE cart SET quantity = %s where user_id = %s and product_id = %s",(new_quantity,user_id,product_id))
         else:
            cursor.execute("INSERT INTO cart(user_id,product_id,quantity) values(%s,%s,%s)",(user_id,product_id,quantity))
         conn.commit()
         cursor.close()
         conn.close()
      return redirect(url_for('view_cart'))
   else:
      return redirect(url_for('login'))

@app.route('/Buy_now/<int:product_id>',methods=['POST','GET'])
def Buy_now(product_id):
   if 'user_status' in session and (session['user_status']=="Registered" or session['user_status']=="logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      try:
         cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
         user_id = cursor.fetchone()
         if user_id:
            user_id = user_id[0]
            if request.method == "POST":
               plot_no = request.form.get('plotno')
               street_address = request.form.get('street')
               area = request.form.get('areaname')
               state = request.form.get('state')
               pincode = request.form.get('pincode')
               country = request.form.get('country')
               quantity = request.form.get('quantity')
               if not plot_no or not street_address or not area or not country or not pincode or not state:
                  return "All fields are required!",400
               address = f"{plot_no},{street_address},{area},{state},{pincode},{country}"
               cursor.execute("""INSERT INTO address(user_id,plot_no,street_address,area,country,state,pincode) 
                              values(%s,%s,%s,%s,%s,%s,%s) 
                              on duplicate key update 
                              plot_no = values(plot_no),
                              street_address=values(street_address),
                              area=values(area),
                              country=values(country),
                              state = values(state),
                              pincode = values(pincode)""",
                              (user_id,plot_no,street_address,area,country,state,pincode)
                           )
               cursor.execute("INSERT INTO orders(user_id,product_id,address,quantity) values(%s,%s,%s,%s)",(user_id,product_id,address,quantity))
               conn.commit()
               cursor.execute("SELECT email from customerdetails where username = %s",(username,))
               email = cursor.fetchone()
               email = email[0]
               msg = Message("Order placed Successfully - Perfect Perfume",sender = "perfectperfumeteam@gmail.com",recipients = [email])
               msg.body = f"Dear {username},\nYour order has been placed. Thankyou for purchasing our product. You will receive your order in two to three days... \n\nRegards,\nPerfect-Perfume"
               mail.send(msg)
               return redirect(url_for('confirmation',product_id=product_id,quantity=quantity))
         return render_template('Buy_now.html',product_id=product_id)
      finally:
         cursor.close()
         conn.close()
   else:
      return redirect(url_for('login'))

@app.route('/Buy_cart',methods=['POST','GET'])
def Buy_cart():
   if 'user_status' in session and (session['user_status'] == "Registered" or session['user_status'] == "logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      try:
         cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
         user_id = cursor.fetchone()
         if user_id:
            user_id = user_id[0]
            if request.method == "POST":
               plot_no = request.form.get('plotno')
               street_address = request.form.get('street')
               area = request.form.get('areaname')
               state = request.form.get('state')
               pincode = request.form.get('pincode')
               country = request.form.get('country')
               if not plot_no or not street_address or not area or not state or not pincode or not country:
                  return "All fields are required!",400
               address(plot_no,street_address,area,state,pincode,country)
               cursor.execute("SELECT email from customerdetails where username = %s",(username,))
               email = cursor.fetchone()
               email = email[0]
               msg = Message("Order placed Successfully - Perfect Perfume",sender = "perfectperfumeteam@gmail.com",recipients = [email])
               msg.body = f"Dear {username},\nYour order has been placed. Thankyou for purchasing our product.You will receive your order in two to three days... \n\nRegards,\nPerfect-Perfume"
               mail.send(msg)
               return redirect(url_for('confirmation_cart'))
            return render_template('Buy_cart.html') 
      finally:
         cursor.close()
         conn.close()
   else:
      return redirect(url_for('login'))

def address(plot_no,street_address,area,state,pincode,country):
   if 'user_status' in session and (session['user_status'] == "Registered" or session['user_status'] == "logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      try:
         cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
         user_id = cursor.fetchone()

         if user_id:
            user_id = user_id[0]
            cursor.execute("""INSERT INTO address(user_id,plot_no,street_address,area,country,state,pincode) 
                                 values(%s,%s,%s,%s,%s,%s,%s) 
                                 on duplicate key update 
                                 plot_no = values(plot_no),
                                 street_address=values(street_address),
                                 area=values(area),
                                 country=values(country),
                                 state = values(state),
                                 pincode = values(pincode)""",
                                 (user_id,plot_no,street_address,area,country,state,pincode)
                              )
            address = f"{plot_no},{street_address},{area},{state},{pincode},{country}"
            cursor.execute("SELECT * from cart where user_id = %s",(user_id,))
            cart_items = cursor.fetchall()
            for item in cart_items:
               product_id = item[2]
               quantity = item[3]
               cursor.execute("INSERT INTO orders(user_id,product_id,quantity,address) VALUES(%s,%s,%s,%s)",(user_id,product_id,quantity,address))
            conn.commit()

      finally:
         cursor.close()
         conn.close()

@app.route('/confirmation_cart',methods=['POST','GET'])
def confirmation_cart():
   if 'user_status' in session and (session['user_status'] == "Registered" or session['user_status'] == "logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
      user_id = cursor.fetchone()
      if user_id:
         user_id = user_id[0]
         cursor.execute("""SELECT p.product_name,p.Ingredients,p.price,c.quantity
                              FROM cart c
                              JOIN product p ON  p.product_id = c.product_id
                              where c.user_id = %s""",(user_id,))
         cart_items = cursor.fetchall()
         grand_total = sum(item[2]*item[3] for item in cart_items)
         cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
         conn.commit()
         cursor.execute("SELECT plot_no,street_address,area,country,state,pincode from address where user_id = %s",(user_id,))
         address_details = cursor.fetchone()
         if address_details:
            address = f"{address_details[0]},{address_details[1]},{address_details[2]},{address_details[3]},{address_details[4]},{address_details[5]}"
         return render_template('confirmation_cart.html',cart_items=cart_items,address=address,grand_total=grand_total)
      cursor.close()
      conn.close()
      if not user_id:
         return "user not found",400
   else:
      return redirect(url_for('login'))
               
@app.route('/confirmation/<int:product_id>/<int:quantity>',methods=['GET'])
def confirmation(product_id,quantity):
   if 'user_status' in session and (session['user_status']=="Registered" or session['user_status']=="logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      try:
         cursor.execute("SELECT product_name,Ingredients,price from product where product_id = %s",(product_id,))
         product_details = cursor.fetchall()
         if product_details:
            product_name,Ingredients,price=product_details[0]
            cursor.execute("""SELECT address.plot_no, address.street_address, address.area,address.state,address.country,address.pincode 
                            FROM address
                            JOIN customerdetails ON address.user_id = customerdetails.user_id
                            where customerdetails.username = %s""",(username,))
            address_details = cursor.fetchall()
            if address_details:
               address = f"{address_details[0][0]},{address_details[0][1]},{address_details[0][2]},{address_details[0][3]},{address_details[0][4]},{address_details[0][5]}"
            else:
               address = "Not available"
            return render_template('confirmation.html',product_id=product_id,product_name=product_name,Ingredients=Ingredients,price=price,address=address,quantity=quantity)
         else:
            return "Product is not available",400
      except mysql.connector.Error as err:
         print(f"Database error: {err}")
         return "An error occurred while processing your request.", 500
      finally:
         cursor.close()
         conn.close()

@app.route('/logout',methods=['POST','GET'])
def logout():
   session.pop('user_status',None)
   return redirect(url_for('index'))
    
@app.route('/Delete_cart',methods=['POST','GET'])
def Delete_cart():
   if 'user_status' in session and (session['user_status'] == "Registered" or session['user_status'] == "logged_in"):
      username = session.get('username')
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT user_id from customerdetails where username = %s",(username,))
      user_id = cursor.fetchone()
      if user_id:
         user_id = user_id[0]
         cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
         conn.commit()
         return redirect(url_for('index'))
      cursor.close()
      conn.close()
      if not user_id:
         return "user not found",400
   else:
      return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug=True)
