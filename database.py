import sqlite3


class LibraryDB:
    def __init__(self, db_name="library.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        self.cursor.executescript(
                '''CREATE TABLE IF NOT EXISTS Authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS Genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS Books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    publisher TEXT,
                    year INTEGER,
                    total_count INTEGER DEFAULT 1,
                    available_count INTEGER DEFAULT 1,
                    author_id INTEGER,
                    FOREIGN KEY (author_id) REFERENCES Authors(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS Book_Genres (
                    book_id INTEGER,
                    genre_id INTEGER,
                    PRIMARY KEY (book_id, genre_id),
                    FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE,
                    FOREIGN KEY (genre_id) REFERENCES Genres(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    phone TEXT
                );

                CREATE TABLE IF NOT EXISTS User_Details (
                    user_id INTEGER PRIMARY KEY,
                    notes TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS Lease_History (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    book_id INTEGER,
                    issue_date TEXT NOT NULL,
                    return_deadline TEXT NOT NULL,
                    actual_return_date TEXT,
                    status TEXT DEFAULT 'на руках',
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (book_id) REFERENCES Books(id)
                )''')
        self.conn.commit()

    def get_all_books(self):
        self.cursor.execute("SELECT * FROM Books")
        return self.cursor.fetchall()

    def get_user_history(self, user_id):
        query = """
        SELECT 
            Books.title, 
            Lease_History.issue_date, 
            Lease_History.actual_return_date 
        FROM Lease_History
        JOIN Books ON Lease_History.book_id = Books.id
        WHERE Lease_History.user_id = ? 
        ORDER BY Lease_History.actual_return_date DESC
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()