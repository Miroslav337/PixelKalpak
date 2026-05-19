import sqlite3
import hashlib
from datetime import date


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class LibraryDB:
    def __init__(self, db_name="library.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        self._migrate()
        self._seed_defaults()

    # ─────────────────────────── SCHEMA ────────────────────────────

    def _create_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS Authors (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS Genres (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS Books (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                title           TEXT    NOT NULL,
                publisher       TEXT,
                year            INTEGER,
                total_count     INTEGER DEFAULT 1,
                available_count INTEGER DEFAULT 1,
                author_id       INTEGER,
                FOREIGN KEY (author_id) REFERENCES Authors(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS Book_Genres (
                book_id  INTEGER,
                genre_id INTEGER,
                PRIMARY KEY (book_id, genre_id),
                FOREIGN KEY (book_id)  REFERENCES Books(id)  ON DELETE CASCADE,
                FOREIGN KEY (genre_id) REFERENCES Genres(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Users (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name         TEXT NOT NULL,
                phone             TEXT,
                gender            TEXT,
                registration_date TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS User_Details (
                user_id   INTEGER PRIMARY KEY,
                notes     TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Admins (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL DEFAULT 'admin',
                created_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Lease_History (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id            INTEGER,
                book_id            INTEGER,
                issue_date         TEXT    NOT NULL,
                return_deadline    TEXT    NOT NULL,
                actual_return_date TEXT,
                status             TEXT    DEFAULT 'на руках',
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (book_id) REFERENCES Books(id)
            );
        ''')
        self.conn.commit()

    def _seed_defaults(self):
        count = self.conn.execute("SELECT COUNT(*) FROM Admins").fetchone()[0]
        if count == 0:
            self.add_admin("admin", "123", "superadmin")

    def _migrate(self):
        """Добавляет новые колонки в уже существующую БД без потери данных."""
        migrations = [
            ("Users", "gender",            "ALTER TABLE Users ADD COLUMN gender TEXT"),
            ("Users", "registration_date", "ALTER TABLE Users ADD COLUMN registration_date TEXT NOT NULL DEFAULT ''"),
        ]
        existing_cols = {}
        for tbl in ["Users", "Books", "Admins", "Lease_History", "User_Details"]:
            cols = self.conn.execute(f"PRAGMA table_info({tbl})").fetchall()
            existing_cols[tbl] = {row[1] for row in cols}

        for table, column, sql in migrations:
            if column not in existing_cols.get(table, set()):
                self.cursor.execute(sql)
        self.conn.commit()

    # ─────────────────────────── AUTHORS ───────────────────────────

    def _get_or_create_author(self, name: str) -> int:
        row = self.cursor.execute(
            "SELECT id FROM Authors WHERE name = ?", (name,)
        ).fetchone()
        if row:
            return row["id"]
        self.cursor.execute("INSERT INTO Authors (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_authors(self):
        return self.conn.execute("SELECT * FROM Authors ORDER BY name").fetchall()

    # ─────────────────────────── GENRES ────────────────────────────

    def add_genre(self, name: str) -> int:
        self.cursor.execute(
            "INSERT OR IGNORE INTO Genres (name) VALUES (?)", (name,)
        )
        self.conn.commit()
        return self.conn.execute(
            "SELECT id FROM Genres WHERE name = ?", (name,)
        ).fetchone()["id"]

    def get_all_genres(self):
        return self.conn.execute("SELECT * FROM Genres ORDER BY name").fetchall()

    # ─────────────────────────── BOOKS ─────────────────────────────

    def add_book(
        self,
        title: str,
        author_name: str = None,
        publisher: str = None,
        year: int = None,
        total_count: int = 1,
        genres: list[str] = None,
    ) -> int:
        """Добавляет книгу. Автора и жанры создаёт автоматически если нужно."""
        author_id = self._get_or_create_author(author_name) if author_name else None

        self.cursor.execute(
            """INSERT INTO Books (title, publisher, year, total_count, available_count, author_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, publisher, year, total_count, total_count, author_id),
        )
        book_id = self.cursor.lastrowid

        for genre_name in (genres or []):
            genre_id = self.add_genre(genre_name)
            self.cursor.execute(
                "INSERT OR IGNORE INTO Book_Genres (book_id, genre_id) VALUES (?, ?)",
                (book_id, genre_id),
            )

        self.conn.commit()
        return book_id

    def edit_book(self, book_id: int, **fields) -> bool:
        """
        Частичное редактирование книги — передавай только то, что нужно изменить.
        Допустимые поля: title, publisher, year, total_count, available_count, author_name, genres.
        """
        allowed = {"title", "publisher", "year", "total_count", "available_count"}

        if "author_name" in fields:
            author_id = self._get_or_create_author(fields.pop("author_name"))
            fields["author_id"] = author_id

        genres = fields.pop("genres", None)

        if "total_count" in fields:
            cur = self.get_book(book_id)
            if cur:
                on_loan = cur["total_count"] - cur["available_count"]
                fields["available_count"] = max(0, int(fields["total_count"]) - on_loan)

        db_fields = {k: v for k, v in fields.items() if k in allowed | {"author_id"}}
        changed = bool(db_fields)
        if db_fields:
            set_clause = ", ".join(f"{col} = ?" for col in db_fields)
            self.cursor.execute(
                f"UPDATE Books SET {set_clause} WHERE id = ?",
                (*db_fields.values(), book_id),
            )

        if genres is not None:
            self.cursor.execute("DELETE FROM Book_Genres WHERE book_id = ?", (book_id,))
            for genre_name in genres:
                genre_id = self.add_genre(genre_name)
                self.cursor.execute(
                    "INSERT OR IGNORE INTO Book_Genres (book_id, genre_id) VALUES (?, ?)",
                    (book_id, genre_id),
                )
            changed = True

        self.conn.commit()
        return changed

    def delete_book(self, book_id: int) -> bool:
        self.cursor.execute("DELETE FROM Lease_History WHERE book_id = ?", (book_id,))
        self.cursor.execute("DELETE FROM Books WHERE id = ?", (book_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_book(self, book_id: int):
        return self.conn.execute(
            """SELECT Books.*, Authors.name AS author_name
               FROM Books
               LEFT JOIN Authors ON Books.author_id = Authors.id
               WHERE Books.id = ?""",
            (book_id,),
        ).fetchone()

    def get_all_books(self):
        return self.conn.execute(
            """SELECT Books.*, Authors.name AS author_name
               FROM Books
               LEFT JOIN Authors ON Books.author_id = Authors.id
               ORDER BY Books.title"""
        ).fetchall()

    def get_book_genres(self, book_id: int):
        return self.conn.execute(
            """SELECT Genres.name FROM Genres
               JOIN Book_Genres ON Genres.id = Book_Genres.genre_id
               WHERE Book_Genres.book_id = ?""",
            (book_id,),
        ).fetchall()

    def search_books(self, query: str):
        like = f"%{query}%"
        return self.conn.execute(
            """SELECT Books.*, Authors.name AS author_name
               FROM Books
               LEFT JOIN Authors ON Books.author_id = Authors.id
               WHERE Books.title LIKE ? OR Authors.name LIKE ?
               ORDER BY Books.title""",
            (like, like),
        ).fetchall()

    # ─────────────────────────── USERS ─────────────────────────────

    def add_user(
        self,
        full_name: str,
        phone: str = None,
        gender: str = None,
    ) -> int:
        """
        Добавляет читателя. Дата регистрации проставляется автоматически.
        gender: 'М' | 'Ж' | None
        """
        reg_date = date.today().isoformat()
        self.cursor.execute(
            "INSERT INTO Users (full_name, phone, gender, registration_date) VALUES (?, ?, ?, ?)",
            (full_name, phone, gender, reg_date),
        )
        user_id = self.cursor.lastrowid
        self.cursor.execute(
            "INSERT INTO User_Details (user_id) VALUES (?)", (user_id,)
        )
        self.conn.commit()
        return user_id

    def edit_user(self, user_id: int, **fields) -> bool:
        """
        Частичное редактирование профиля читателя.
        Допустимые поля: full_name, phone, gender.
        """
        allowed = {"full_name", "phone", "gender"}
        db_fields = {k: v for k, v in fields.items() if k in allowed}
        if not db_fields:
            return False
        set_clause = ", ".join(f"{col} = ?" for col in db_fields)
        self.cursor.execute(
            f"UPDATE Users SET {set_clause} WHERE id = ?",
            (*db_fields.values(), user_id),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def edit_user_notes(self, user_id: int, notes: str) -> bool:
        self.cursor.execute(
            "UPDATE User_Details SET notes = ? WHERE user_id = ?",
            (notes, user_id),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def set_user_active(self, user_id: int, is_active: bool) -> bool:
        self.cursor.execute(
            "UPDATE User_Details SET is_active = ? WHERE user_id = ?",
            (int(is_active), user_id),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        active = self.conn.execute(
            "SELECT book_id FROM Lease_History WHERE user_id = ? AND status = 'на руках'",
            (user_id,)
        ).fetchall()
        for row in active:
            self.cursor.execute(
                "UPDATE Books SET available_count = available_count + 1 WHERE id = ?",
                (row["book_id"],)
            )
        self.cursor.execute("DELETE FROM Lease_History WHERE user_id = ?", (user_id,))
        self.cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_user(self, user_id: int):
        return self.conn.execute(
            """SELECT Users.*, User_Details.notes, User_Details.is_active
               FROM Users
               LEFT JOIN User_Details ON Users.id = User_Details.user_id
               WHERE Users.id = ?""",
            (user_id,),
        ).fetchone()

    def get_all_users(self):
        return self.conn.execute(
            """SELECT Users.*, User_Details.notes, User_Details.is_active
               FROM Users
               LEFT JOIN User_Details ON Users.id = User_Details.user_id
               ORDER BY Users.full_name"""
        ).fetchall()

    def search_users(self, query: str):
        like = f"%{query}%"
        return self.conn.execute(
            """SELECT Users.*, User_Details.notes, User_Details.is_active
               FROM Users
               LEFT JOIN User_Details ON Users.id = User_Details.user_id
               WHERE Users.full_name LIKE ? OR Users.phone LIKE ?
               ORDER BY Users.full_name""",
            (like, like),
        ).fetchall()

    def get_user_history(self, user_id: int):
        return self.conn.execute(
            """SELECT Books.title, Lease_History.issue_date,
                      Lease_History.return_deadline, Lease_History.actual_return_date,
                      Lease_History.status
               FROM Lease_History
               JOIN Books ON Lease_History.book_id = Books.id
               WHERE Lease_History.user_id = ?
               ORDER BY Lease_History.issue_date DESC""",
            (user_id,),
        ).fetchall()

    # ─────────────────────────── ADMINS ────────────────────────────

    def add_admin(self, username: str, password: str, role: str = "admin") -> int:
        """
        role: 'superadmin' | 'admin'
        Пароль хранится как SHA-256 хеш.
        """
        if role not in ("superadmin", "admin"):
            raise ValueError("role должен быть 'superadmin' или 'admin'")
        self.cursor.execute(
            "INSERT INTO Admins (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, _hash(password), role, date.today().isoformat()),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def check_admin_password(self, username: str, password: str) -> bool:
        row = self.conn.execute(
            "SELECT password_hash FROM Admins WHERE username = ?", (username,)
        ).fetchone()
        return bool(row and row["password_hash"] == _hash(password))

    def edit_admin(self, admin_id: int, **fields) -> bool:
        """
        Допустимые поля: username, password (будет захеширован), role.
        """
        allowed = {"username", "role"}
        db_fields = {k: v for k, v in fields.items() if k in allowed}
        if "password" in fields:
            db_fields["password_hash"] = _hash(fields["password"])
        if not db_fields:
            return False
        set_clause = ", ".join(f"{col} = ?" for col in db_fields)
        self.cursor.execute(
            f"UPDATE Admins SET {set_clause} WHERE id = ?",
            (*db_fields.values(), admin_id),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_admin(self, admin_id: int) -> bool:
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM Admins WHERE role = 'superadmin'"
        ).fetchone()
        target = self.conn.execute(
            "SELECT role FROM Admins WHERE id = ?", (admin_id,)
        ).fetchone()
        if target and target["role"] == "superadmin" and row["cnt"] <= 1:
            raise ValueError("Нельзя удалить последнего суперадмина")
        self.cursor.execute("DELETE FROM Admins WHERE id = ?", (admin_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_admin(self, username: str):
        return self.conn.execute(
            "SELECT id, username, role, created_at FROM Admins WHERE username = ?",
            (username,),
        ).fetchone()

    def get_all_admins(self):
        return self.conn.execute(
            "SELECT id, username, role, created_at FROM Admins ORDER BY role, username"
        ).fetchall()

    # ─────────────────────────── LEASES ────────────────────────────

    def issue_book(self, user_id: int, book_id: int, return_deadline: str) -> int:
        """Выдать книгу. return_deadline — строка 'YYYY-MM-DD'."""
        row = self.conn.execute(
            "SELECT available_count FROM Books WHERE id = ?", (book_id,)
        ).fetchone()
        if not row or row["available_count"] < 1:
            raise ValueError("Книга недоступна для выдачи")
        self.cursor.execute(
            """INSERT INTO Lease_History (user_id, book_id, issue_date, return_deadline)
               VALUES (?, ?, ?, ?)""",
            (user_id, book_id, date.today().isoformat(), return_deadline),
        )
        self.cursor.execute(
            "UPDATE Books SET available_count = available_count - 1 WHERE id = ?",
            (book_id,),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def return_book(self, lease_id: int) -> bool:
        """Зафиксировать возврат книги."""
        row = self.conn.execute(
            "SELECT book_id, status FROM Lease_History WHERE id = ?", (lease_id,)
        ).fetchone()
        if not row or row["status"] == "возвращена":
            return False
        self.cursor.execute(
            """UPDATE Lease_History
               SET actual_return_date = ?, status = 'возвращена'
               WHERE id = ?""",
            (date.today().isoformat(), lease_id),
        )
        self.cursor.execute(
            "UPDATE Books SET available_count = available_count + 1 WHERE id = ?",
            (row["book_id"],),
        )
        self.conn.commit()
        return True

    def get_active_leases(self):
        return self.conn.execute(
            """SELECT Lease_History.id, Users.full_name, Books.title,
                      Lease_History.issue_date, Lease_History.return_deadline,
                      Lease_History.user_id, Lease_History.book_id
               FROM Lease_History
               JOIN Users ON Lease_History.user_id = Users.id
               JOIN Books ON Lease_History.book_id = Books.id
               WHERE Lease_History.status = 'на руках'
               ORDER BY Lease_History.return_deadline"""
        ).fetchall()

    def get_overdue_leases(self):
        today = date.today().isoformat()
        return self.conn.execute(
            """SELECT Lease_History.id, Users.full_name, Books.title,
                      Lease_History.issue_date, Lease_History.return_deadline,
                      Lease_History.user_id, Lease_History.book_id
               FROM Lease_History
               JOIN Users ON Lease_History.user_id = Users.id
               JOIN Books ON Lease_History.book_id = Books.id
               WHERE Lease_History.status = 'на руках' AND Lease_History.return_deadline < ?
               ORDER BY Lease_History.return_deadline""",
            (today,),
        ).fetchall()
