from flask import Flask, request, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import sqlite3
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

@app.route('/templates/images/<filename>')
def send_image(filename):
    return send_from_directory('templates/images', filename)

class PaymentForm(FlaskForm):
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16, message='Card number should be 16 digits')])
    card_holder = StringField('Card Holder', validators=[DataRequired()])
    expiry_date = StringField('Expiry Date', validators=[DataRequired(), Length(min=5, max=5, message='Expiry date should be in MM/YY format')])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=3, message='CVV should be 3 digits')])
    submit = SubmitField('Submit Payment')
# Database initialization
def init_db():
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')
    # Create payments table with a foreign key reference to users
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount_owed REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/',methods=['GET','POST'])
def home():
    # Insert a new user for demonstration (adjust as needed for your application)
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (name) VALUES (?)', ('Demo User',))
    user_id = c.lastrowid
    
    # Randomize the amount owed for demonstration
    amount_owed = round(random.uniform(10.0, 100.0), 2)
    
    # Insert a new payment record with a randomized amount owed for the new user
    c.execute('INSERT INTO payments (user_id, amount_owed) VALUES (?, ?)', (user_id, amount_owed))
    conn.commit()
    payment_id = c.lastrowid
    conn.close()
    form = PaymentForm()
    if form.validate_on_submit():
        # Handle the form submission here, e.g. send the payment to your payment processor
        pass
    # Render the HTML template with user_id, payment_id, and amount_owed
    return render_template('payment.html', form=form, user_id=user_id, payment_id=payment_id, amount_owed=amount_owed)

@app.route('/payment/<int:user_id>', methods=['GET'])
def get_amount_owed(user_id):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute('SELECT amount_owed FROM payments WHERE user_id = ?', (user_id,))
    amount = c.fetchone()
    conn.close()
    if amount:
        return jsonify({'user_id': user_id, 'amount_owed': amount[0]})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/update_payment/<int:user_id>', methods=['POST'])
def update_payment(user_id):
    amount_owed = round(random.uniform(10.0, 100.0), 2)
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    # Ensure the user exists
    user_exists = c.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,)).fetchone()
    if not user_exists:
        return jsonify({'error': 'User not found'}), 404
    
    # Update the payment amount for the user
    c.execute('UPDATE payments SET amount_owed = ? WHERE user_id = ?', (amount_owed, user_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Payment updated successfully', 'user_id': user_id, 'amount_owed': amount_owed})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True, port=5001)
