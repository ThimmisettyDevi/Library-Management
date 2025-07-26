import sqlite3

# Step 1: Connect to the database (must match with app.py)
conn = sqlite3.connect("library.db")
cur = conn.cursor()

# Step 2: Drop existing tables (for development/testing only)
cur.execute("DROP TABLE IF EXISTS transactions")
cur.execute("DROP TABLE IF EXISTS books")
cur.execute("DROP TABLE IF EXISTS users")

# Step 3: Create 'users' table
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

# Step 5: Create 'books' table
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

# Step 6: Create 'transactions' table
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

# Step 7: Insert 10 sample books
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
    ("Crime and Punishment", "Fyodor Dostoevsky", "ISBN010", 4),
    ("Wings of Fire", "A.P.J. Abdul Kalam", "ISBN011", 5),
    ("The White Tiger", "Aravind Adiga", "ISBN012", 3),
    ("Train to Pakistan", "Khushwant Singh", "ISBN013", 4),
    ("Midnight's Children", "Salman Rushdie", "ISBN014", 3),
    ("The God of Small Things", "Arundhati Roy", "ISBN015", 4),
    ("Gitanjali", "Rabindranath Tagore", "ISBN016", 5),
    ("Yayati", "V.S. Khandekar", "ISBN017", 3),
    ("Parva", "S.L. Bhyrappa", "ISBN018", 2),
    ("Chanakya Neeti", "Chanakya", "ISBN019", 6),
    ("Ramayana", "Valmiki (Telugu Translation)", "ISBN020", 3),

    # Telugu Books
    ("Maha Prasthanam", "Sri Sri", "ISBN021", 4),
    ("Kanyasulkam", "Gurajada Apparao", "ISBN022", 3),
    ("Amuktamalyada", "Krishna Devaraya", "ISBN023", 2),
    ("Antarmukham", "Yandamoori Veerendranath", "ISBN024", 5),
    ("Ashtavakra Gita", "Translated in Telugu", "ISBN025", 3),

    # Hindi Books
    ("Godaan", "Munshi Premchand", "ISBN026", 5),
    ("Gunahon Ka Devta", "Dharamvir Bharati", "ISBN027", 4),
    ("Rashmirathi", "Ramdhari Singh Dinkar", "ISBN028", 3),
    ("Raag Darbari", "Sri Lal Sukla", "ISBN029", 4),
    ("Nirmala", "Munshi Premchand", "ISBN030", 3),
    # 📖 Fiction & Novels
    ("The Kite Runner", "Khaled Hosseini", "ISBN031", 4),
    ("Norwegian Wood", "Haruki Murakami", "ISBN032", 3),
    ("The Book Thief", "Markus Zusak", "ISBN033", 5),
    ("Life of Pi", "Yann Martel", "ISBN034", 4),
    ("A Thousand Splendid Suns", "Khaled Hosseini", "ISBN035", 4),
    ("Veronika Decides to Die", "Paulo Coelho", "ISBN036", 3),
    ("The Palace of Illusions", "Chitra Banerjee Divakaruni", "ISBN037", 5),

    # 👧 Children’s Books
    ("Chacha Chaudhary", "Pran Kumar Sharma", "ISBN038", 10),
    ("Panchatantra Tales", "Vishnu Sharma", "ISBN039", 8),
    ("Tenali Raman Stories", "Various", "ISBN040", 7),
    ("Akbar and Birbal", "Folklore", "ISBN041", 6),
    ("Malgudi Days", "R.K. Narayan", "ISBN042", 5),
    ("Tinkle Digest", "Various", "ISBN043", 12),
    ("Harry Potter and the Chamber of Secrets", "J.K. Rowling", "ISBN044", 4),

    # 🕉️ Hindu Mythology
    ("Bhagavad Gita", "Vyasa", "ISBN045", 5),
    ("Ramayana", "Valmiki", "ISBN046", 4),
    ("Mahabharata", "Vyasa", "ISBN047", 3),
    ("Shiva Purana", "Unknown", "ISBN048", 2),

    # ☪️ Islamic Mythology
    ("Stories of the Prophets", "Ibn Kathir", "ISBN049", 4),
    ("The Life of Prophet Muhammad", "Martin Lings", "ISBN050", 3),

    # ✝️ Christian Mythology
    ("The Bible: Illustrated Stories", "Various", "ISBN051", 4),
    ("The Chronicles of Narnia", "C.S. Lewis", "ISBN052", 4),

    # 🕍 Jewish Mythology
    ("Legends of the Jews", "Louis Ginzberg", "ISBN053", 2),

    # 🕉️ Buddhist Texts & Stories
    ("The Dhammapada", "Lord Buddha", "ISBN054", 3),
    ("Jataka Tales", "Various", "ISBN055", 6),

    # 🛕 Jain Mythology
    ("Tirthankara Stories", "Various", "ISBN056", 2)
]
cur.executemany("INSERT INTO books (title, author, isbn, quantity) VALUES (?, ?, ?, ?)", sample_books)
print("10 sample books inserted.")

# Step 8: Commit and close
conn.commit()
conn.close()
print("Database initialized successfully.")
