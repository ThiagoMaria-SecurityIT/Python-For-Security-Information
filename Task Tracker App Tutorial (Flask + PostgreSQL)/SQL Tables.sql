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
