import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta # pip install python-dateutil
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color_code = db.Column(db.String(7), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color_code': self.color_code
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    priority = db.Column(db.String(10), nullable=False) # High, Medium, Low
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Not Started') # Not Started, In Progress, Completed, Blocked, Deferred
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    frequency = db.Column(db.String(20), nullable=True) # Daily, Weekly, Monthly, Annually, Bi-weekly
    last_done = db.Column(db.Date, nullable=True)
    next_due = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name, # Access category name via relationship
            'category_color': self.category.color_code,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'is_recurring': self.is_recurring,
            'frequency': self.frequency,
            'last_done': self.last_done.isoformat() if self.last_done else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# --- Helper function for recurring tasks ---
def calculate_next_due_date(last_done_date, frequency):
    if not last_done_date or not frequency:
        return None

    if frequency == 'Daily':
        return last_done_date + timedelta(days=1)
    elif frequency == 'Weekly':
        return last_done_date + timedelta(weeks=1)
    elif frequency == 'Bi-weekly':
        return last_done_date + timedelta(weeks=2)
    elif frequency == 'Monthly':
        return last_done_date + relativedelta(months=1)
    elif frequency == 'Annually':
        return last_done_date + relativedelta(years=1)
    else:
        return None

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    new_task = Task(
        name=data['name'],
        category_id=data['category_id'],
        priority=data['priority'],
        due_date=date.fromisoformat(data['due_date']) if data.get('due_date') else None,
        status=data.get('status', 'Not Started'),
        is_recurring=data.get('is_recurring', False),
        frequency=data.get('frequency'),
        last_done=date.fromisoformat(data['last_done']) if data.get('last_done') else None,
        next_due=date.fromisoformat(data['next_due']) if data.get('next_due') else None
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.name = data.get('name', task.name)
    task.category_id = data.get('category_id', task.category_id)
    task.priority = data.get('priority', task.priority)
    task.due_date = date.fromisoformat(data['due_date']) if data.get('due_date') else None
    task.status = data.get('status', task.status)
    task.is_recurring = data.get('is_recurring', task.is_recurring)
    task.frequency = data.get('frequency', task.frequency)
    task.last_done = date.fromisoformat(data['last_done']) if data.get('last_done') else None
    task.next_due = date.fromisoformat(data['next_due']) if data.get('next_due') else None

    # Special handling for recurring tasks when status changes to 'Completed'
    if task.is_recurring and data.get('status') == 'Completed' and task.status != 'Completed':
        task.last_done = date.today() # Mark today as last done
        task.next_due = calculate_next_due_date(task.last_done, task.frequency)
        # Optionally, reset status to 'Not Started' for the *next* iteration
        # task.status = 'Not Started' # This would require a separate "complete and reset" action or logic

    db.session.commit()
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204 # No Content

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories])

# --- Run the app ---
if __name__ == '__main__':
    # Create database tables if they don't exist (based on models)
    # This should only be run ONCE after setting up the DB schema manually,
    # or if you let SQLAlchemy manage schema creation entirely.
    # For this tutorial, we created tables manually, so this is for initial setup if needed.
    with app.app_context():
        db.create_all() # This creates tables based on models if they don't exist.
                        # It won't modify existing tables, so it's safe to run.
        # Ensure initial categories are present if db.create_all() was used to create tables
        if not Category.query.first():
            initial_categories = [
                Category(name='Work', color_code='#FFD700'),
                Category(name='Home', color_code='#90EE90'),
                Category(name='Health', color_code='#87CEEB'),
                Category(name='Finance', color_code='#FFB6C1'),
                Category(name='Study', color_code='#3F7AB5')
            ]
            db.session.bulk_save_objects(initial_categories)
            db.session.commit()

    app.run(debug=True) # debug=True enables auto-reloading and better error messages
