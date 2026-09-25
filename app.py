from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = "campusfind-secret-key"


# -----------------------------
# UPLOAD SETTINGS
# -----------------------------

UPLOAD_FOLDER = os.path.join("static", "uploads")

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# -----------------------------
# DATABASE SETUP
# -----------------------------

def init_db():

    conn = sqlite3.connect("database.db")

    # USERS TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ITEMS TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Active',
            image TEXT,
            user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()


def update_database():

    conn = sqlite3.connect("database.db")

    columns = conn.execute(
        "PRAGMA table_info(items)"
    ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    # Add status column if it doesn't exist
    if "status" not in column_names:

        conn.execute("""
            ALTER TABLE items
            ADD COLUMN status TEXT DEFAULT 'Active'
        """)

    # Add image column if it doesn't exist
    if "image" not in column_names:

        conn.execute("""
            ALTER TABLE items
            ADD COLUMN image TEXT
        """)

    # Add user_id column if it doesn't exist
    if "user_id" not in column_names:

        conn.execute("""
            ALTER TABLE items
            ADD COLUMN user_id INTEGER
        """)

    conn.commit()
    conn.close()


# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# HOW IT WORKS
# -----------------------------

@app.route("/how-it-works")
def how_it_works():

    return render_template("how_it_works.html")


# -----------------------------
# SIGN UP
# -----------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip()

        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")

        try:

            conn.execute("""
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
            """, (
                name,
                email,
                hashed_password
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "signup.html",
                error="An account with this email already exists."
            )

        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# -----------------------------
# LOGIN
# -----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()

        password = request.form["password"]

        conn = sqlite3.connect("database.db")

        conn.row_factory = sqlite3.Row

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# -----------------------------
# REPORT ITEM
# -----------------------------

@app.route("/report", methods=["GET", "POST"])
def report():

    # User must be logged in
    if "user_id" not in session:

        return redirect(url_for("login"))

    if request.method == "POST":

        item_type = request.form["type"]

        item_name = request.form["item_name"].strip()

        category = request.form["category"].strip()

        location = request.form["location"].strip()

        date = request.form["date"]

        description = request.form["description"].strip()

        image = request.files.get("image")

        image_filename = None

        # -----------------------------
        # IMAGE UPLOAD
        # -----------------------------

        if image and image.filename and allowed_file(image.filename):

            filename = secure_filename(image.filename)

            base, extension = os.path.splitext(filename)

            counter = 1

            while os.path.exists(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            ):

                filename = f"{base}_{counter}{extension}"

                counter += 1

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            image_filename = filename

        # -----------------------------
        # SAVE ITEM
        # -----------------------------

        conn = sqlite3.connect("database.db")

        conn.execute("""
            INSERT INTO items
            (
                type,
                item_name,
                category,
                location,
                date,
                description,
                image,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_type,
            item_name,
            category,
            location,
            date,
            description,
            image_filename,
            session["user_id"]
        ))

        conn.commit()

        conn.close()

        return redirect(url_for("items"))

    return render_template("report.html")


# -----------------------------
# FIND ITEMS
# -----------------------------

@app.route("/items")
def items():

    search = request.args.get(
        "search",
        ""
    ).strip()

    item_type = request.args.get(
        "type",
        ""
    ).strip()

    category = request.args.get(
        "category",
        ""
    ).strip()

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    # Start query
    query = """
        SELECT *
        FROM items
        WHERE 1 = 1
    """

    params = []

    # -----------------------------
    # SEARCH FILTER
    # -----------------------------

    if search:

        query += """
            AND (
                LOWER(TRIM(item_name)) LIKE LOWER(?)
                OR LOWER(TRIM(location)) LIKE LOWER(?)
                OR LOWER(TRIM(category)) LIKE LOWER(?)
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value
        ])

    # -----------------------------
    # LOST / FOUND FILTER
    # -----------------------------

    if item_type:

        query += """
            AND LOWER(TRIM(type)) = LOWER(TRIM(?))
        """

        params.append(item_type)

    # -----------------------------
    # CATEGORY FILTER
    # -----------------------------

    if category:

        query += """
            AND LOWER(TRIM(category)) = LOWER(TRIM(?))
        """

        params.append(category)

    # Newest items first
    query += """
        ORDER BY id DESC
    """

    items = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return render_template(
        "items.html",
        items=items,
        search=search,
        item_type=item_type,
        category=category
    )


# -----------------------------
# MY REPORTS
# -----------------------------

@app.route("/my-reports")
def my_reports():

    if "user_id" not in session:

        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    reports = conn.execute("""
        SELECT *
        FROM items
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "my_reports.html",
        reports=reports
    )


# -----------------------------
# ITEM DETAILS
# -----------------------------

@app.route("/item/<int:item_id>")
def item_details(item_id):

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    item = conn.execute("""
        SELECT
            items.*,
            users.name AS reporter_name,
            users.email AS reporter_email
        FROM items

        LEFT JOIN users
        ON items.user_id = users.id

        WHERE items.id = ?
    """, (
        item_id,
    )).fetchone()

    conn.close()

    if not item:

        return redirect(url_for("items"))

    return render_template(
        "item_details.html",
        item=item
    )


# -----------------------------
# CONTACT REPORTER
# -----------------------------

@app.route("/contact/<int:item_id>")
def contact_reporter(item_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    item = conn.execute("""
        SELECT
            items.*,
            users.name AS reporter_name,
            users.email AS reporter_email
        FROM items

        LEFT JOIN users
        ON items.user_id = users.id

        WHERE items.id = ?
    """, (
        item_id,
    )).fetchone()

    conn.close()

    if not item:

        return redirect(url_for("items"))

    # Don't allow someone to contact themselves
    if (
        item["user_id"] is not None
        and item["user_id"] == session["user_id"]
    ):

        return redirect(
            url_for(
                "item_details",
                item_id=item_id
            )
        )

    # If no reporter email exists
    if not item["reporter_email"]:

        return redirect(
            url_for(
                "item_details",
                item_id=item_id
            )
        )

    return render_template(
        "contact.html",
        item=item
    )


# -----------------------------
# MARK ITEM AS RESOLVED
# -----------------------------

@app.route("/resolve/<int:item_id>")
def resolve_item(item_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    item = conn.execute("""
        SELECT *
        FROM items
        WHERE id = ?
    """, (
        item_id,
    )).fetchone()

    if not item:

        conn.close()

        return redirect(url_for("items"))

    # Only owner can resolve their report
    if item["user_id"] != session["user_id"]:

        conn.close()

        return redirect(
            url_for(
                "item_details",
                item_id=item_id
            )
        )

    conn.execute("""
        UPDATE items

        SET status = 'Resolved'

        WHERE id = ?
    """, (
        item_id,
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for(
            "item_details",
            item_id=item_id
        )
    )


# -----------------------------
# EDIT ITEM
# -----------------------------

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    item = conn.execute("""
        SELECT *
        FROM items
        WHERE id = ?
    """, (
        item_id,
    )).fetchone()

    if not item:

        conn.close()

        return redirect(url_for("items"))

    # Only owner can edit
    if item["user_id"] != session["user_id"]:

        conn.close()

        return redirect(
            url_for(
                "item_details",
                item_id=item_id
            )
        )

    if request.method == "POST":

        item_type = request.form["type"]

        item_name = request.form["item_name"].strip()

        category = request.form["category"].strip()

        location = request.form["location"].strip()

        date = request.form["date"]

        description = request.form["description"].strip()

        conn.execute("""
            UPDATE items

            SET
                type = ?,
                item_name = ?,
                category = ?,
                location = ?,
                date = ?,
                description = ?

            WHERE id = ?
        """, (
            item_type,
            item_name,
            category,
            location,
            date,
            description,
            item_id
        ))

        conn.commit()

        conn.close()

        return redirect(
            url_for(
                "item_details",
                item_id=item_id
            )
        )

    conn.close()

    return render_template(
        "edit.html",
        item=item
    )


# -----------------------------
# DELETE ITEM
# -----------------------------

@app.route("/delete/<int:item_id>")
def delete_item(item_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    item = conn.execute("""
        SELECT *
        FROM items
        WHERE id = ?
    """, (
        item_id,
    )).fetchone()

    if not item:

        conn.close()

        return redirect(url_for("items"))

    # Only owner can delete
    if item["user_id"] != session["user_id"]:

        conn.close()

        return redirect(
            url_for(
                "item_details",
                item_id=item_id
            )
        )

    # Delete uploaded image
    if item["image"]:

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            item["image"]
        )

        if os.path.exists(image_path):

            os.remove(image_path)

    # Delete database record
    conn.execute("""
        DELETE FROM items
        WHERE id = ?
    """, (
        item_id,
    ))

    conn.commit()

    conn.close()

    return redirect(url_for("items"))


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":

    init_db()

    update_database()

    app.run(debug=True)