# Tutorial for Python to build a basic task tracker web application using Flask (a Python web framework) and PostgreSQL.

This tutorial will cover:

1.  **Setting up your environment:** Installing Python, PostgreSQL, and necessary libraries.
2.  **Database Schema:** Designing and creating your PostgreSQL tables.
3.  **Python Backend (Flask):**
    *   Connecting to PostgreSQL.
    *   Defining data models.
    *   Implementing API endpoints for creating, reading, updating, and deleting tasks.
    *   Handling categories and priorities.
    *   Basic logic for recurring tasks.
4.  **Basic Frontend (HTML/CSS/JavaScript):** A simple web page to interact with your backend.

**Important Notes before we start:**

*   **Complexity:** Building a full-featured application is a significant undertaking. This tutorial will provide a *functional prototype* that demonstrates the core concepts. It will be simplified in terms of error handling, user interface design, and advanced features (like real-time updates, complex recurring task logic, or user authentication).
*   **Security:** This code is for learning purposes and is *not* production-ready. It lacks proper security measures (e.g., input validation, authentication, robust error handling).
*   **User Interface:** The frontend will be very basic HTML and JavaScript, focusing on functionality rather than aesthetics.
*   **Streak/Progress Bar:** The "Streak" and visual "Progress Bar" from your examples are more complex to implement purely with basic database and web app logic. For this tutorial, we'll focus on the core task management. "Progress" will be reflected by the `Status` field.

---

## Task Tracker Application Tutorial (Flask + PostgreSQL)

### Step 1: Prerequisites and Setup

Before you write any code, you need to set up your development environment.

#### 1.1 Install Python

If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/). Python 3.8+ is recommended.

#### 1.2 Install PostgreSQL

Download and install PostgreSQL from [postgresql.org/download/](https://www.postgresql.org/download/). During installation, remember the password you set for the `postgres` user.

#### 1.3 Create a PostgreSQL Database

Open your terminal or command prompt and connect to PostgreSQL using `psql` (usually installed with PostgreSQL).

```bash
psql -U postgres
```

Enter your `postgres` user password when prompted.

Now, create a new database and a new user for your application:

```sql
CREATE DATABASE task_tracker_db;
CREATE USER task_tracker_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE task_tracker_db TO task_tracker_user;
\q
```
**Remember to replace `'your_strong_password'` with a strong password.**

#### 1.4 Create Project Directory and Virtual Environment

Create a new folder for your project and set up a Python virtual environment. This keeps your project's dependencies isolated.

```bash
mkdir task_tracker_app
cd task_tracker_app
python -m venv venv
```

Activate the virtual environment:

*   **On Windows:** `venv\Scripts\activate`
*   **On macOS/Linux:** `source venv/bin/activate`

You should see `(venv)` at the beginning of your terminal prompt.

#### 1.5 Install Python Libraries

With your virtual environment active, install the necessary Python packages:

```bash
pip install Flask Flask-SQLAlchemy psycopg2-binary python-dotenv
```

*   `Flask`: The web framework.
*   `Flask-SQLAlchemy`: An ORM (Object-Relational Mapper) that simplifies database interactions with SQLAlchemy.
*   `psycopg2-binary`: PostgreSQL adapter for Python.
*   `python-dotenv`: To manage environment variables (like your database password) securely.

### Step 2: Database Schema (PostgreSQL)

We'll define two tables: `categories` and `tasks`.

#### 2.1 `categories` Table

This table will store your predefined categories and their associated color codes.

| Column Name | Data Type | Constraints | Description |
| :---------- | :-------- | :---------- | :---------- |
| `id`        | `SERIAL`  | `PRIMARY KEY` | Unique identifier for the category. |
| `name`      | `VARCHAR(50)` | `NOT NULL`, `UNIQUE` | Name of the category (e.g., 'Work', 'Home'). |
| `color_code`| `VARCHAR(7)` | `NOT NULL` | Hex color code (e.g., '#FFD700'). |

#### 2.2 `tasks` Table

This table will store all your task details.

| Column Name | Data Type | Constraints | Description |
| :---------- | :-------- | :---------- | :---------- |
| `id`        | `SERIAL`  | `PRIMARY KEY` | Unique identifier for the task. |
| `name`      | `TEXT`    | `NOT NULL` | Description of the task. |
| `category_id`| `INTEGER` | `NOT NULL`, `FOREIGN KEY` | Links to the `categories` table. |
| `priority`  | `VARCHAR(10)` | `NOT NULL` | 'High', 'Medium', 'Low'. |
| `due_date`  | `DATE`    | `NULLABLE` | When the task is due. |
| `status`    | `VARCHAR(20)` | `NOT NULL` | 'Not Started', 'In Progress', 'Completed', 'Blocked', 'Deferred'. |
| `is_recurring`| `BOOLEAN` | `NOT NULL` | True if the task is recurring. |
| `frequency` | `VARCHAR(20)` | `NULLABLE` | 'Daily', 'Weekly', 'Monthly', 'etc.' (if recurring). |
| `last_done` | `DATE`    | `NULLABLE` | Last completion date for recurring tasks. |
| `next_due`  | `DATE`    | `NULLABLE` | Next due date for recurring tasks (calculated). |
| `created_at`| `TIMESTAMP` | `DEFAULT NOW()` | When the task was created. |
| `updated_at`| `TIMESTAMP` | `DEFAULT NOW()` | When the task was last updated. |

#### 2.3 SQL Commands to Create Tables

You can execute these commands using `psql` after connecting to your `task_tracker_db` database:

```bash
psql -U task_tracker_user -d task_tracker_db
```
Enter your `task_tracker_user` password.

```sql
-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color_code VARCHAR(7) NOT NULL
);

-- Insert initial categories
INSERT INTO categories (name, color_code) VALUES
('Work', '#FFD700'),
('Home', '#90EE90'),
('Health', '#87CEEB'),
('Finance', '#FFB6C1'),
('Study', '#3F7AB5');

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    priority VARCHAR(10) NOT NULL,
    due_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Not Started',
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    frequency VARCHAR(20),
    last_done DATE,
    next_due DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add a trigger to update 'updated_at' automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

\q
```

### Step 3: Python Backend (Flask)

#### 3.1 Project Structure

Create the following files and folders in your `task_tracker_app` directory:

```
task_tracker_app/
├── venv/
├── .env
├── app.py
├── requirements.txt
└── templates/
    └── index.html
```

#### 3.2 `.env` file

Create a file named `.env` in your `task_tracker_app` directory and add your database connection string. **Replace `your_strong_password` with the actual password you set.**

```
DATABASE_URL="postgresql://task_tracker_user:your_strong_password@localhost/task_tracker_db"
```

#### 3.3 `requirements.txt` file

Create a file named `requirements.txt` in your `task_tracker_app` directory. This lists your project's dependencies.

```
Flask
Flask-SQLAlchemy
psycopg2-binary
python-dotenv
```

#### 3.4 `app.py` (Flask Application)

This is the core of your backend.

```python
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
```

**Note on `db.create_all()`:** In this tutorial, we manually created the tables and inserted initial categories using SQL. `db.create_all()` will only create tables if they don't exist. If you want SQLAlchemy to manage your schema entirely, you would skip the manual `CREATE TABLE` SQL commands and rely solely on `db.create_all()`. For this tutorial, it's included as a safety net and to ensure categories are populated if you started with an empty DB.

### Step 4: Basic Frontend (HTML/CSS/JavaScript)

Create a `templates` folder in your `task_tracker_app` directory, and inside it, create `index.html`.

#### `templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Task Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #0056b3;
        }
        form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #e9e9e9;
        }
        form label {
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }
        form input[type="text"],
        form input[type="date"],
        form select {
            width: calc(100% - 10px);
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        form input[type="checkbox"] {
            margin-top: 10px;
        }
        form button {
            grid-column: span 2;
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        form button:hover {
            background-color: #0056b3;
        }
        .task-list {
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .task-row {
            background-color: white;
        }
        .task-row:hover {
            background-color: #f9f9f9;
        }
        .task-row.completed {
            text-decoration: line-through;
            color: #888;
            background-color: #e0ffe0;
        }
        .actions button {
            padding: 5px 10px;
            margin-right: 5px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .actions .edit-btn {
            background-color: #ffc107;
            color: black;
        }
        .actions .delete-btn {
            background-color: #dc3545;
            color: white;
        }
        .actions .edit-btn:hover { background-color: #e0a800; }
        .actions .delete-btn:hover { background-color: #c82333; }

        .category-label {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Task Tracker</h1>

        <h2>Add New Task</h2>
        <form id="taskForm">
            <div>
                <label for="taskName">Task Name:</label>
                <input type="text" id="taskName" required>
            </div>
            <div>
                <label for="category">Category:</label>
                <select id="category" required></select>
            </div>
            <div>
                <label for="priority">Priority:</label>
                <select id="priority" required>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                </select>
            </div>
            <div>
                <label for="dueDate">Due Date:</label>
                <input type="date" id="dueDate">
            </div>
            <div>
                <label for="status">Status:</label>
                <select id="status" required>
                    <option value="Not Started">Not Started</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Blocked">Blocked</option>
                    <option value="Deferred">Deferred</option>
                </select>
            </div>
            <div>
                <label for="isRecurring">Recurring:</label>
                <input type="checkbox" id="isRecurring">
            </div>
            <div id="recurringOptions" style="display: none;">
                <label for="frequency">Frequency:</label>
                <select id="frequency">
                    <option value="">-- Select --</option>
                    <option value="Daily">Daily</option>
                    <option value="Weekly">Weekly</option>
                    <option value="Bi-weekly">Bi-weekly</option>
                    <option value="Monthly">Monthly</option>
                    <option value="Annually">Annually</option>
                </select>
                <label for="lastDone">Last Done (for recurring):</label>
                <input type="date" id="lastDone">
            </div>
            <button type="submit">Add Task</button>
        </form>

        <h2>My Tasks</h2>
        <div class="task-list">
            <table>
                <thead>
                    <tr>
                        <th>Task</th>
                        <th>Category</th>
                        <th>Priority</th>
                        <th>Due Date</th>
                        <th>Status</th>
                        <th>Recurring</th>
                        <th>Frequency</th>
                        <th>Last Done</th>
                        <th>Next Due</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="tasksTableBody">
                    <!-- Tasks will be loaded here by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const API_BASE_URL = ''; // Flask serves from root
        const taskForm = document.getElementById('taskForm');
        const tasksTableBody = document.getElementById('tasksTableBody');
        const categorySelect = document.getElementById('category');
        const isRecurringCheckbox = document.getElementById('isRecurring');
        const recurringOptionsDiv = document.getElementById('recurringOptions');
        let categories = []; // To store fetched categories

        // --- Fetch Categories and Populate Dropdown ---
        async function fetchCategories() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/categories`);
                categories = await response.json();
                categorySelect.innerHTML = ''; // Clear existing options
                categories.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.id;
                    option.textContent = cat.name;
                    categorySelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error fetching categories:', error);
            }
        }

        // --- Toggle Recurring Options Visibility ---
        isRecurringCheckbox.addEventListener('change', () => {
            recurringOptionsDiv.style.display = isRecurringCheckbox.checked ? 'block' : 'none';
        });

        // --- Fetch and Display Tasks ---
        async function fetchTasks() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/tasks`);
                const tasks = await response.json();
                tasksTableBody.innerHTML = ''; // Clear existing tasks
                tasks.forEach(task => {
                    const row = tasksTableBody.insertRow();
                    row.dataset.taskId = task.id; // Store task ID on the row
                    row.classList.add('task-row');
                    if (task.status === 'Completed') {
                        row.classList.add('completed');
                    }

                    const categoryColor = task.category_color || '#ccc'; // Default if not found

                    row.innerHTML = `
                        <td>${task.name}</td>
                        <td><span class="category-label" style="background-color: ${categoryColor};">${task.category_name}</span></td>
                        <td>${task.priority}</td>
                        <td>${task.due_date || 'N/A'}</td>
                        <td>${task.status}</td>
                        <td>${task.is_recurring ? 'Yes' : 'No'}</td>
                        <td>${task.frequency || 'N/A'}</td>
                        <td>${task.last_done || 'N/A'}</td>
                        <td>${task.next_due || 'N/A'}</td>
                        <td class="actions">
                            <button class="edit-btn" onclick="editTask(${task.id})">Edit</button>
                            <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
                        </td>
                    `;
                });
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }
        }

        // --- Add/Update Task ---
        taskForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const taskId = taskForm.dataset.editingTaskId; // Check if we are editing
            const method = taskId ? 'PUT' : 'POST';
            const url = taskId ? `${API_BASE_URL}/api/tasks/${taskId}` : `${API_BASE_URL}/api/tasks`;

            const taskData = {
                name: document.getElementById('taskName').value,
                category_id: parseInt(document.getElementById('category').value),
                priority: document.getElementById('priority').value,
                due_date: document.getElementById('dueDate').value || null,
                status: document.getElementById('status').value,
                is_recurring: document.getElementById('isRecurring').checked,
                frequency: document.getElementById('frequency').value || null,
                last_done: document.getElementById('lastDone').value || null,
                next_due: null // Backend will calculate for recurring on completion
            };

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(taskData),
                });

                if (response.ok) {
                    taskForm.reset(); // Clear form
                    delete taskForm.dataset.editingTaskId; // Remove editing state
                    recurringOptionsDiv.style.display = 'none'; // Hide recurring options
                    await fetchTasks(); // Refresh task list
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.message || response.statusText}`);
                }
            } catch (error) {
                console.error('Error submitting task:', error);
                alert('An error occurred while submitting the task.');
            }
        });

        // --- Edit Task (Populate Form) ---
        async function editTask(id) {
            try {
                const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`);
                const task = await response.json();

                document.getElementById('taskName').value = task.name;
                document.getElementById('category').value = task.category_id;
                document.getElementById('priority').value = task.priority;
                document.getElementById('dueDate').value = task.due_date;
                document.getElementById('status').value = task.status;
                document.getElementById('isRecurring').checked = task.is_recurring;
                document.getElementById('frequency').value = task.frequency || '';
                document.getElementById('lastDone').value = task.last_done;

                recurringOptionsDiv.style.display = task.is_recurring ? 'block' : 'none';

                taskForm.dataset.editingTaskId = id; // Store ID to indicate editing mode
                document.querySelector('#taskForm button[type="submit"]').textContent = 'Update Task';
            } catch (error) {
                console.error('Error fetching task for edit:', error);
            }
        }

        // --- Delete Task ---
        async function
---
## Part 2

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Task Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #0056b3;
        }
        form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #e9e9e9;
        }
        form label {
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }
        form input[type="text"],
        form input[type="date"],
        form select {
            width: calc(100% - 10px);
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        form input[type="checkbox"] {
            margin-top: 10px;
        }
        form button {
            grid-column: span 2;
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        form button:hover {
            background-color: #0056b3;
        }
        .task-list {
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .task-row {
            background-color: white;
        }
        .task-row:hover {
            background-color: #f9f9f9;
        }
        .task-row.completed {
            text-decoration: line-through;
            color: #888;
            background-color: #e0ffe0;
        }
        .actions button {
            padding: 5px 10px;
            margin-right: 5px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .actions .edit-btn {
            background-color: #ffc107;
            color: black;
        }
        .actions .delete-btn {
            background-color: #dc3545;
            color: white;
        }
        .actions .edit-btn:hover { background-color: #e0a800; }
        .actions .delete-btn:hover { background-color: #c82333; }

        .category-label {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Task Tracker</h1>

        <h2>Add New Task</h2>
        <form id="taskForm">
            <div>
                <label for="taskName">Task Name:</label>
                <input type="text" id="taskName" required>
            </div>
            <div>
                <label for="category">Category:</label>
                <select id="category" required></select>
            </div>
            <div>
                <label for="priority">Priority:</label>
                <select id="priority" required>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                </select>
            </div>
            <div>
                <label for="dueDate">Due Date:</label>
                <input type="date" id="dueDate">
            </div>
            <div>
                <label for="status">Status:</label>
                <select id="status" required>
                    <option value="Not Started">Not Started</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Blocked">Blocked</option>
                    <option value="Deferred">Deferred</option>
                </select>
            </div>
            <div>
                <label for="isRecurring">Recurring:</label>
                <input type="checkbox" id="isRecurring">
            </div>
            <div id="recurringOptions" style="display: none;">
                <label for="frequency">Frequency:</label>
                <select id="frequency">
                    <option value="">-- Select --</option>
                    <option value="Daily">Daily</option>
                    <option value="Weekly">Weekly</option>
                    <option value="Bi-weekly">Bi-weekly</option>
                    <option value="Monthly">Monthly</option>
                    <option value="Annually">Annually</option>
                </select>
                <label for="lastDone">Last Done (for recurring):</label>
                <input type="date" id="lastDone">
            </div>
            <button type="submit">Add Task</button>
        </form>

        <h2>My Tasks</h2>
        <div class="task-list">
            <table>
                <thead>
                    <tr>
                        <th>Task</th>
                        <th>Category</th>
                        <th>Priority</th>
                        <th>Due Date</th>
                        <th>Status</th>
                        <th>Recurring</th>
                        <th>Frequency</th>
                        <th>Last Done</th>
                        <th>Next Due</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="tasksTableBody">
                    <!-- Tasks will be loaded here by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const API_BASE_URL = ''; // Flask serves from root
        const taskForm = document.getElementById('taskForm');
        const tasksTableBody = document.getElementById('tasksTableBody');
        const categorySelect = document.getElementById('category');
        const isRecurringCheckbox = document.getElementById('isRecurring');
        const recurringOptionsDiv = document.getElementById('recurringOptions');
        let categories = []; // To store fetched categories

        // --- Fetch Categories and Populate Dropdown ---
        async function fetchCategories() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/categories`);
                categories = await response.json();
                categorySelect.innerHTML = ''; // Clear existing options
                categories.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.id;
                    option.textContent = cat.name;
                    categorySelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error fetching categories:', error);
            }
        }

        // --- Toggle Recurring Options Visibility ---
        isRecurringCheckbox.addEventListener('change', () => {
            recurringOptionsDiv.style.display = isRecurringCheckbox.checked ? 'block' : 'none';
        });

        // --- Fetch and Display Tasks ---
        async function fetchTasks() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/tasks`);
                const tasks = await response.json();
                tasksTableBody.innerHTML = ''; // Clear existing tasks
                tasks.forEach(task => {
                    const row = tasksTableBody.insertRow();
                    row.dataset.taskId = task.id; // Store task ID on the row
                    row.classList.add('task-row');
                    if (task.status === 'Completed') {
                        row.classList.add('completed');
                    }

                    const categoryColor = task.category_color || '#ccc'; // Default if not found

                    row.innerHTML = `
                        <td>${task.name}</td>
                        <td><span class="category-label" style="background-color: ${categoryColor};">${task.category_name}</span></td>
                        <td>${task.priority}</td>
                        <td>${task.due_date || 'N/A'}</td>
                        <td>${task.status}</td>
                        <td>${task.is_recurring ? 'Yes' : 'No'}</td>
                        <td>${task.frequency || 'N/A'}</td>
                        <td>${task.last_done || 'N/A'}</td>
                        <td>${task.next_due || 'N/A'}</td>
                        <td class="actions">
                            <button class="edit-btn" onclick="editTask(${task.id})">Edit</button>
                            <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
                        </td>
                    `;
                });
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }
        }

        // --- Add/Update Task ---
        taskForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const taskId = taskForm.dataset.editingTaskId; // Check if we are editing
            const method = taskId ? 'PUT' : 'POST';
            const url = taskId ? `${API_BASE_URL}/api/tasks/${taskId}` : `${API_BASE_URL}/api/tasks`;

            const taskData = {
                name: document.getElementById('taskName').value,
                category_id: parseInt(document.getElementById('category').value),
                priority: document.getElementById('priority').value,
                due_date: document.getElementById('dueDate').value || null,
                status: document.getElementById('status').value,
                is_recurring: document.getElementById('isRecurring').checked,
                frequency: document.getElementById('frequency').value || null,
                last_done: document.getElementById('lastDone').value || null,
                next_due: null // Backend will calculate for recurring on completion
            };

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(taskData),
                });

                if (response.ok) {
                    taskForm.reset(); // Clear form
                    delete taskForm.dataset.editingTaskId; // Remove editing state
                    document.querySelector('#taskForm button[type="submit"]').textContent = 'Add Task'; // Reset button text
                    recurringOptionsDiv.style.display = 'none'; // Hide recurring options
                    await fetchTasks(); // Refresh task list
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.message || response.statusText}`);
                }
            } catch (error) {
                console.error('Error submitting task:', error);
                alert('An error occurred while submitting the task.');
            }
        });

        // --- Edit Task (Populate Form) ---
        async function editTask(id) {
            try {
                const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`);
                const task = await response.json();

                document.getElementById('taskName').value = task.name;
                document.getElementById('category').value = task.category_id;
                document.getElementById('priority').value = task.priority;
                document.getElementById('dueDate').value = task.due_date;
                document.getElementById('status').value = task.status;
                document.getElementById('isRecurring').checked = task.is_recurring;
                document.getElementById('frequency').value = task.frequency || '';
                document.getElementById('lastDone').value = task.last_done;

                recurringOptionsDiv.style.display = task.is_recurring ? 'block' : 'none';

                taskForm.dataset.editingTaskId = id; // Store ID to indicate editing mode
                document.querySelector('#taskForm button[type="submit"]').textContent = 'Update Task';
            } catch (error) {
                console.error('Error fetching task for edit:', error);
            }
        }

        // --- Delete Task ---
        async function deleteTask(id) {
            if (confirm('Are you sure you want to delete this task?')) {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
                        method: 'DELETE',
                    });

                    if (response.ok) {
                        await fetchTasks(); // Refresh task list
                    } else {
                        const errorData = await response.json();
                        alert(`Error: ${errorData.message || response.statusText}`);
                    }
                } catch (error) {
                    console.error('Error deleting task:', error);
                    alert('An error occurred while deleting the task.');
                }
            }
        }

        // --- Initial Load ---
        document.addEventListener('DOMContentLoaded', async () => {
            await fetchCategories();
            await fetchTasks();
        });
    </script>
</body>
</html>
```

---

### Step 5: Run the Application

1.  **Ensure your virtual environment is active.** If not, activate it:
    *   **On Windows:** `venv\Scripts\activate`
    *   **On macOS/Linux:** `source venv/bin/activate`

2.  **Run the Flask application:**

    ```bash
    python app.py
    ```

    You should see output similar to this:

    ```
     * Serving Flask app 'app'
     * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: XXX-XXX-XXX
    ```

3.  **Open your web browser** and navigate to `http://127.0.0.1:5000`.

You should now see your simple task tracker interface. You can add new tasks, select categories and priorities, set due dates, mark them as recurring, and update/delete them.

### Further Enhancements (Beyond this Tutorial)

This is a basic functional prototype. Here are some ideas for how you could expand it:

*   **Improved UI/UX:** Use a CSS framework (like Bootstrap or Tailwind CSS) or a JavaScript framework (React, Vue, Angular) for a more polished and interactive user interface.
*   **User Authentication:** Add user login/registration so multiple users can have their own task lists.
*   **Advanced Recurring Logic:** Implement more sophisticated handling for recurring tasks, such as automatically creating the next instance when one is completed, or handling tasks that recur on specific days of the week/month.
*   **Filtering and Sorting:** Add controls to the frontend to filter tasks by category, priority, status, or sort them by due date.
*   **Search Functionality:** Allow users to search for tasks by name.
*   **Reminders/Notifications:** Integrate with email or push notification services.
*   **Error Handling:** More robust error handling and user feedback in both the backend and frontend.
*   **Deployment:** Learn how to deploy your Flask application to a production server (e.g., Heroku, Render, AWS, DigitalOcean).
*   **Testing:** Write unit and integration tests for your backend and frontend.
*   **Progress Tracking:** Implement the "Streak" and visual "Progress" bars using more complex logic or frontend libraries.

This should give you a solid foundation to build upon! Let me know if you have any specific questions about parts of the code or want to explore any of these enhancements further.

## Made with love and Manus AI
This tutorial has parts and was made with the help of AI. 
The AI to create the codes was Manus AI and is under review by me from July 01, 2025 to July 07, 2025.  

## About the Author   

**Thiago Maria - From Brazil to the World 🌎**  
*Senior Security Information Professional | Passionate Programmer | AI Developer*

With a professional background in security analysis and a deep passion for programming, I created this Github acc to share some knowledge about security information & compliance, cybersecurity, Python and AI development practices. Most of my work here focuses on implementing security-first approaches in developer tools while maintaining usability.

Lets Connect:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/thiago-cequeira-99202239/)  
[![Hugging Face](https://img.shields.io/badge/🤗Hugging_Face-AI_projects-yellow)](https://huggingface.co/ThiSecur)

 
## Ways to Contribute:   
You can send me messages or emails by any of my social media or directly here!
Want to see more upgrades? Help me keep it updated!    
 [![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-red)](https://github.com/sponsors/ThiagoMaria-SecurityIT) 
