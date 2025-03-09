from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, current_app
import logging
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.models import db, User, TennisCourt, Booking, Match
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Routes
# Add current datetime to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    """Homepage showing nearby tennis courts"""
    return render_template('index.html')

@app.route('/courts')
def courts():
    """API endpoint to get nearby tennis courts"""
    try:
        # Get query parameters (for future implementation of location-based filtering)
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        
        # For now, return all courts
        courts = TennisCourt.query.all()
        
        if not courts:
            current_app.logger.warning("No tennis courts found in database")
            return jsonify([])
        
        # Convert courts to JSON format
        courts_data = []
        for court in courts:
            try:
                court_data = {
                    'id': court.id,
                    'name': court.name,
                    'address': court.address,
                    'latitude': float(court.latitude),
                    'longitude': float(court.longitude),
                    'price_per_hour': float(court.price_per_hour)
                }
                courts_data.append(court_data)
            except (ValueError, AttributeError) as e:
                current_app.logger.error(f"Error processing court {court.id}: {str(e)}")
                continue
        
        return jsonify(courts_data)
    except Exception as e:
        current_app.logger.error(f"Error fetching courts: {str(e)}")
        return jsonify({'error': 'Failed to fetch tennis courts'}), 500

@app.route('/book/<int:court_id>', methods=['GET', 'POST'])
@login_required
def book_court(court_id):
    """Book a tennis court"""
    court = TennisCourt.query.get_or_404(court_id)
    
    if request.method == 'POST':
        try:
            booking = Booking(
                user_id=current_user.id,
                tennis_court_id=court_id,
                booking_time=request.form['booking_time'],
                duration=int(request.form['duration']),
                status='confirmed'
            )
            db.session.add(booking)
            db.session.commit()
            flash('Court booked successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Error booking court. Please try again.', 'error')
            
    return render_template('booking.html', court=court)

@app.route('/setup-match', methods=['GET', 'POST'])
@login_required
def setup_match():
    """Set up a match with another player"""
    if request.method == 'POST':
        try:
            opponent = User.query.filter_by(email=request.form['opponent_email']).first()
            if not opponent:
                flash('Opponent not found.', 'error')
                return redirect(url_for('setup_match'))
                
            match = Match(
                court_id=request.form['court_id'],
                player1_id=current_user.id,
                player2_id=opponent.id,
                match_time=request.form['match_time'],
                duration=int(request.form['duration'])
            )
            db.session.add(match)
            db.session.commit()
            flash('Match setup successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Error setting up match. Please try again.', 'error')
            
    courts = TennisCourt.query.all()
    return render_template('match_setup.html', courts=courts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            user = User(
                username=request.form['username'],
                email=request.form['email']
            )
            user.set_password(request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error during registration. Please try again.', 'error')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=Config.DEBUG)
