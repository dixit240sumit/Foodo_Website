from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# MySQL database connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='sumitdixit240',  # Replace with your MySQL password
            database='food_ordering'
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Fetch all menu items from the database
def get_menu_items():
    connection = get_db_connection()
    if connection is None:
        return []
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu_items")
    menu_items = cursor.fetchall()
    cursor.close()
    connection.close()
    return menu_items

# Add an item to the cart in the session
def add_item_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = []  # Initialize the cart if it's not already present
    session['cart'].append(item_id)

# Fetch cart items from the database based on the session
def get_cart_items():
    if 'cart' not in session or len(session['cart']) == 0:
        return []
    
    connection = get_db_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu_items WHERE id IN (%s)", (', '.join(map(str, session['cart'])),))
    cart_items = cursor.fetchall()
    cursor.close()
    connection.close()
    return cart_items

# Remove an item from the cart (based on session)
def remove_item_from_cart(item_id):
    if 'cart' in session and item_id in session['cart']:
        session['cart'].remove(item_id)

# User login
def user_login(username, password):
    connection = get_db_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

# User registration
def user_register(username, password, email):
    connection = get_db_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
    connection.commit()
    cursor.close()
    connection.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    menu_items = get_menu_items()  # Fetch menu items from MySQL
    return render_template('index.html', menu_items=menu_items)

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    add_item_to_cart(item_id)  # Add item to session-based cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart_items = get_cart_items()  # Fetch items in the cart from the database
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    remove_item_from_cart(item_id)  # Remove item from session-based cart
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    if 'cart' not in session or len(session['cart']) == 0:
        return redirect(url_for('view_cart'))
    cart_items = get_cart_items()  # Fetch items in the cart
    return render_template('payment.html', cart_items=cart_items)

@app.route('/order_confirmation')
def order_confirmation():
    if 'cart' not in session or len(session['cart']) == 0:
        return redirect(url_for('view_cart'))
    
    cart_items = get_cart_items()
    # Here, you can process payment and save order details in the database
    # After the order is placed, clear the session cart
    session.pop('cart', None)
    
    return render_template('order_confirmation.html')

@app.route('/foodologin', methods=['GET', 'POST'])
def foodologin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_login(username, password)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            return "Login failed. Please check your credentials."
    return render_template('foodologin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_register(username, password, email)
        return redirect(url_for('foodologin'))
    return render_template('sign_up.html')

@app.route('/payment_done')
def payment_done():
    return render_template('payment_done.html')

@app.route('/back_to_my_order')
def back_to_my_order():
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)
