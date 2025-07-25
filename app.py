from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'library.db'

# --- Utility Function ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- Routes ---
@app.route('/')
def home():
    return render_template('entry.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'member')

        is_admin = session.get('role') == 'admin'
        if role == 'admin' and not is_admin:
            return "Only admins can create new admins!"

        try:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                             (name, email, password, role))
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already registered!"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT id, name, role FROM users WHERE name=? AND password=?", (username, password))
            user = cur.fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/member_dashboard')
        else:
            error = "Invalid credentials"

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Access Denied!"
    return render_template('admin_dashboard.html')

@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if session.get('role') != 'admin':
        return redirect('/login')

    with get_db_connection() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            action = request.form.get('action')
            book_id = request.form.get('book_id')
            title = request.form.get('title')
            author = request.form.get('author')
            year = request.form.get('year')

            if action == 'add':
                cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
            elif action == 'edit':
                cursor.execute("UPDATE books SET title=?, author=?, year=? WHERE id=?", (title, author, year, book_id))
            elif action == 'delete':
                cursor.execute("DELETE FROM books WHERE id=?", (book_id,))

            conn.commit()
            return redirect('/books')

        books = cursor.execute("SELECT * FROM books").fetchall()
    return render_template('manage_books.html', books=books)

@app.route('/manage_members')
def manage_members():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect('/login')

    conn = get_db_connection()
    members = conn.execute("SELECT * FROM users WHERE role = 'member'").fetchall()
    conn.close()
    return render_template('manage_members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        with get_db_connection() as conn:
            conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'member')",
                         (name, email, password))
            conn.commit()

        return redirect('/manage_members')

    return render_template('add_member.html')

@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    if session.get('role') != 'admin':
        return redirect('/login')

    with get_db_connection() as conn:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            conn.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, member_id))
            conn.commit()
            return redirect('/manage_members')

        member = conn.execute("SELECT name, email FROM users WHERE id=?", (member_id,)).fetchone()

    return render_template('edit_member.html', member=member)

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized action', 'danger')
        return redirect('/login')

    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()
    flash('Member deleted successfully!', 'success')
    return redirect('/manage_members')

@app.route('/transactions')
def transactions():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect('/login')

    conn = get_db_connection()
    issued_books = conn.execute("SELECT * FROM transactions").fetchall()
    conn.close()
    return render_template('transactions.html', issued_books=issued_books)

@app.route('/issue_book', methods=['POST'])
def issue_book():
    member_id = request.form['member_id']
    book_id = request.form['book_id']
    issue_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    conn.execute("INSERT INTO transactions (member_id, book_id, issue_date) VALUES (?, ?, ?)",
                 (member_id, book_id, issue_date))
    conn.commit()
    conn.close()
    flash('Book issued successfully!', 'success')
    return redirect('/transactions')

@app.route('/return_book', methods=['POST'])
def return_book():
    member_id = request.form['member_id']
    book_id = request.form['book_id']

    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE member_id = ? AND book_id = ?", (member_id, book_id))
    conn.commit()
    conn.close()
    flash('Book returned successfully!', 'success')
    return redirect('/transactions')

@app.route('/member_dashboard')
def member_dashboard():
    if 'user_id' not in session or session.get('role') != 'member':
        flash('Unauthorized access', 'danger')
        return redirect('/login')

    conn = get_db_connection()
    user = conn.execute("SELECT name FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('member_dashboard.html', name=user['name'])

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        quantity = request.form['quantity']

        conn = get_db_connection()
        conn.execute("INSERT INTO books (title, author, isbn, quantity) VALUES (?, ?, ?, ?)",
                     (title, author, isbn, quantity))
        conn.commit()
        conn.close()
        flash('Book added successfully!', 'success')
        return redirect('/books')

    return render_template('add_book.html')

@app.route('/my_books')
def my_books():
    if 'user_id' not in session or session.get('role') != 'member':
        flash('Unauthorized access', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    books = conn.execute("""
        SELECT t.id as transaction_id, b.title, b.author, t.issue_date, t.due_date 
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.member_id = ? AND t.return_date IS NULL
    """, (user_id,)).fetchall()
    conn.close()

    return render_template('my_books.html', books=books)

@app.route('/return_book/<int:transaction_id>', methods=['POST'])
def return_transaction_book(transaction_id):
    if 'user_id' not in session or session.get('role') != 'member':
        flash('Unauthorized', 'danger')
        return redirect('/login')

    conn = get_db_connection()
    conn.execute("UPDATE transactions SET return_date = DATE('now') WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()
    flash('Book returned successfully!', 'success')
    return redirect('/my_books')

@app.route('/reports')
def reports():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect('/login')

    conn = get_db_connection()
    total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_members = conn.execute("SELECT COUNT(*) FROM users WHERE role='member'").fetchone()[0]
    total_issued = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

    top_books = conn.execute("""
        SELECT t.book_id, b.title, COUNT(t.book_id) as count
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        GROUP BY t.book_id
        ORDER BY count DESC
        LIMIT 5
    """).fetchall()
    conn.close()

    return render_template('reports.html', 
                           total_books=total_books,
                           total_members=total_members,
                           total_issued=total_issued,
                           top_books=top_books)

@app.route('/search_books')
def search_books():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect('/login')

    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return render_template('search_books.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)
