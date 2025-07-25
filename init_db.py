import sqlite3

# Step 1: Connect to the database (must match with app.py)
conn = sqlite3.connect("library.db")
cur = conn.cursor()

# Step 2: Drop existing tables (for development/testing purposes only)
cur.execute("DROP TABLE IF EXISTS transactions")
cur.execute("DROP TABLE IF EXISTS books")
cur.execute("DROP TABLE IF EXISTS users")

# Step 3: Create 'users' table with role constraint
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'member'))
)
''')

# Step 4: Insert default admin users
admin_users = [
    ('Admin One', 'admin1@library.com', 'admin123', 'admin'),
    ('Admin Two', 'admin2@library.com', 'admin123', 'admin')
]
cur.executemany("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", admin_users)
print("Admin users inserted.")

# Step 5: Create 'books' table with isbn and quantity
cur.execute('''
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    quantity INTEGER DEFAULT 1
)
''')
print("Books table created.")

# Step 6: Create 'transactions' table (for book issue/return)
cur.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    issue_date TEXT,
    due_date TEXT,
    return_date TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (member_id) REFERENCES users(id)
)
''')
print("Transactions table created.")

sample_books = [
    ("The Alchemist", "Paulo Coelho", "ISBN001", 5),
    ("1984", "George Orwell", "ISBN002", 4),
    ("To Kill a Mockingbird", "Harper Lee", "ISBN003", 6),
    ("The Great Gatsby", "F. Scott Fitzgerald", "ISBN004", 3),
    ("Pride and Prejudice", "Jane Austen", "ISBN005", 7),
    ("The Catcher in the Rye", "J.D. Salinger", "ISBN006", 4),
    ("The Hobbit", "J.R.R. Tolkien", "ISBN007", 5),
    ("Moby Dick", "Herman Melville", "ISBN008", 2),
    ("War and Peace", "Leo Tolstoy", "ISBN009", 3),
    ("Crime and Punishment", "Fyodor Dostoevsky", "ISBN010", 4)
]

cur.executemany("INSERT INTO books (title, author, isbn, quantity) VALUES (?, ?, ?, ?)", sample_books)


print("10 sample books inserted successfully.")

# Step 7: Commit and close
conn.commit()
conn.close()
print("Database initialized successfully.")
