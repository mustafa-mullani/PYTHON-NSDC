from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, date, timedelta


app = Flask(__name__)
app.secret_key = "event_secret_key"
DB = "event_management.db"

def get_db():
    conn = sqlite3.connect(DB, timeout=30,
            check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

ADMIN_ACCOUNTS = {
    "maratha@gmail.com": {
        "password": "maratha123",
        "hotel": "Maratha"
    },
    "sayaji@gmail.com": {
        "password": "sayaji123",
        "hotel": "Sayaji"
    },
    "vrishali@gmail.com": {
        "password": "vrishali123",
        "hotel": "Vrishali"
    }
}

MENU_PRICES = {
    "Maratha": {"Veg": 500, "Chicken": 600, "Mutton": 700},
    "Sayaji": {"Veg": 700, "Chicken": 800, "Mutton": 900},
    "Vrishali": {"Veg": 400, "Chicken": 500, "Mutton": 600}
}

HALL_CAPACITY = {
    # Maratha
    "Emrald": {"min": 80, "max": 150},
    "Pearl": {"min": 10, "max": 30},
    "Ruby": {"min": 30, "max": 70},

    # Vrishali
    "Platinum Palace": {"min": 100, "max": 350},
    "Ivory": {"min": 30, "max": 60},

    # Sayaji
    "Dwarka Boardroom": {"min": 20, "max": 30},
    "Nalanda Conference Room": {"min": 50, "max": 70},
    "Megh Malhar": {"min": 80, "max": 120},
    "Basant Banquet": {"min": 180, "max": 220},
    "Sky Green Banquet": {"min": 50, "max": 90}
}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/hotel")
def hotel():
    return render_template("hotel.html")

@app.route("/maratha")
def maratha():
    session["hotel"] = "Maratha"
    return render_template("maratha.html")

@app.route("/sayaji")
def sayaji():
    session["hotel"] = "Sayaji"
    return render_template("sayaji.html")

@app.route("/vrishali")
def vrishali():
    session["hotel"] = "Vrishali"
    return render_template("vrishali.html")

@app.route("/select_hall/<hall_name>")
def select_hall(hall_name):
    session["hall"] = hall_name
    return redirect(url_for("book"))


@app.route("/book", methods=["GET", "POST"])
def book():
    if "hall" not in session or "hotel" not in session:
        return redirect(url_for("hotel"))
    
    if request.method == "POST":
        session.pop("booking_completed", None)

        event_date = request.form["date"]
        start_time = request.form["s_time"]
        end_time = request.form["e_time"]
        capacity = int(request.form["capacity"])
        hall_name = session["hall"]

        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        if event_date < date.today():
            flash("❌ Event date cannot be in the past")
            return render_template("book.html", today=date.today())
        
        start_dt = datetime.strptime(
            f"{event_date} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(
            f"{event_date} {end_time}", "%Y-%m-%d %H:%M")

        if end_dt <= start_dt:
            flash("❌ End time must be after start time")
            return render_template("book.html", today=date.today())

        if end_dt - start_dt < timedelta(hours=4):
            flash("❌ Event duration must be at least 4 hours")
            return render_template("book.html", today=date.today())
        
        hall_rule = HALL_CAPACITY.get(hall_name)

        if hall_rule:
            min_cap = hall_rule["min"]
            max_cap = hall_rule["max"]

            if capacity < min_cap or capacity > max_cap:
                flash(
                    f"❌ Capacity must be between {min_cap} and {max_cap} persons for {hall_name}"
                )
                return render_template("book.html", today=date.today())
        conn = get_db()
        conflict = conn.execute("""
            SELECT 1 FROM bookings
            WHERE hotel_name = ?
              AND hall_name = ?
              AND event_date = ?
              AND start_time < ?
              AND end_time > ?
        """, (
            session["hotel"],
            session["hall"],
            event_date,
            end_time,
            start_time
        )).fetchone()
        if conflict:
            flash("❌ Booking not available for this date & time")
            return render_template("book.html", today=date.today())

        session["booking"] = {
            "event_name": request.form["event_name"],
            "event_type": request.form["event_type"],
            "event_date": request.form["date"],
            "start_time": start_time,
            "end_time": end_time,
            "capacity": capacity,
            "description": request.form["description"]
        }
        return redirect(url_for("hotel_menu"))
    return render_template("book.html", today=date.today())


@app.route("/hotel_menu")
def hotel_menu():
    if session["hotel"] == "Maratha":
        return render_template("hmr_menu.html")
    if session["hotel"] == "Sayaji":
        return render_template("sayaji_menu.html")
    if session["hotel"] == "Vrishali":
        return render_template("vrishali_menu.html")
    return redirect(url_for("home"))


@app.route("/maratha/veg_menu", methods=["GET", "POST"])
def maratha_veg_menu():
    if request.method == "POST":
        session["menu_type"] = "Veg"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("hmr_veg_menu.html")


@app.route("/maratha/chicken_menu", methods=["GET", "POST"])
def maratha_chicken_menu():
    if request.method == "POST":
        session["menu_type"] = "Chicken"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("hmr_chicken_menu.html")


@app.route("/maratha/mutton_menu", methods=["GET", "POST"])
def maratha_mutton_menu():
    if request.method == "POST":
        session["menu_type"] = "Mutton"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("hmr_mutton_menu.html")


@app.route("/sayaji/veg_menu", methods=["GET", "POST"])
def sayaji_veg_menu():
    if request.method == "POST":
        session["menu_type"] = "Veg"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("sayaji_veg_menu.html")


@app.route("/sayaji/chicken_menu", methods=["GET", "POST"])
def sayaji_chicken_menu():
    if request.method == "POST":
        session["menu_type"] = "Chicken"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("sayaji_chicken_menu.html")


@app.route("/sayaji/mutton_menu", methods=["GET", "POST"])
def sayaji_mutton_menu():
    if request.method == "POST":
        session["menu_type"] = "Mutton"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("sayaji_mutton_menu.html")


@app.route("/vrishali/veg_menu", methods=["GET", "POST"])
def vrishali_veg_menu():
    if request.method == "POST":
        session["menu_type"] = "Veg"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("vrishali_veg_menu.html")


@app.route("/vrishali/chicken_menu", methods=["GET", "POST"])
def vrishali_chicken_menu():
    if request.method == "POST":
        session["menu_type"] = "Chicken"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("vrishali_chicken_menu.html")


@app.route("/vrishali/mutton_menu", methods=["GET", "POST"])
def vrishali_mutton_menu():
    if request.method == "POST":
        session["menu_type"] = "Mutton"
        session["menu_items"] = dict(request.form)

        if session.get("user_logged_in"):
            return redirect(url_for("save_booking"))
        else:
            return redirect(url_for("login"))
    return render_template("vrishali_mutton_menu.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        ph_number = request.form["ph_number"]

        if not ph_number.isdigit() or len(ph_number) !=10:
            flash("Phone number must be exactly 10 digits", "error")
            return render_template("register.html")

        conn = get_db()

        # Check duplicate email
        existing = conn.execute(
            "SELECT 1 FROM register WHERE email=?",
            (email,)
        ).fetchone()

        if existing:
            flash("Email already registered", "error")
            return render_template("register.html")
        
        existing = conn.execute(
            "SELECT 1 FROM register WHERE username=?",
            (username,)
        ).fetchone()

        if existing:
            flash("Username already registered", "error")
            return render_template("register.html")
        
        # Insert user
        conn.execute("""
            INSERT INTO register (username, email, password, ph_number)
            VALUES (?, ?, ?, ?)
        """, (username, email, password, ph_number))

        conn.commit()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

         # ADMIN LOGIN
        admin = ADMIN_ACCOUNTS.get(email)
        if admin and admin["password"] == password:
            session.clear()
            session["admin_logged_in"] = True
            session["admin_hotel"] = admin["hotel"]
            return redirect(url_for("admin_dashboard"))
        
        # USER LOGIN
        conn = get_db()
        user = conn.execute("""
            SELECT * FROM register
            WHERE email=? AND password=?
        """, (email, password)).fetchone()

        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["user_logged_in"] = True
            flash("Login Successful !","success")

            if "booking" in session and "menu_items" in session:
                return redirect(url_for("save_booking"))
            return redirect(next_page or url_for("home"))
        return render_template("login.html", next=next_page)
    return render_template("login.html", next=next_page)


@app.route("/save_booking")
def save_booking():
    if not session.get("user_logged_in"):
        flash("Please login to complete booking", "warning")
        return redirect(url_for("login"))
    
    if session.get("booking_completed"):
        flash("Booking already submitted", "error ")
        return redirect(url_for("my_bookings"))
    required = ["hotel", "hall", "booking", "menu_type", "menu_items"]
    
    for key in required:
        if key not in session:
            flash("Incomplete booking session", "error")
            return redirect(url_for("home"))

    if "user_id" not in session:
        flash(" You must login first", "Warning")
        return redirect(url_for("login"))
    
    conn = get_db()

    cur = conn.execute("""
        INSERT INTO bookings
        (user_id, hotel_name, hall_name, event_name, event_type,
         event_date, start_time, end_time, menu_type,
         capacity, description, status, payment_status, event_status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 'unpaid', 'ongoing')
    """, (
        session["user_id"],
        session["hotel"],
        session["hall"],
        session["booking"]["event_name"],
        session["booking"]["event_type"],
        session["booking"]["event_date"],
        session["booking"]["start_time"],
        session["booking"]["end_time"],
        session["menu_type"],
        session["booking"]["capacity"],
        session["booking"]["description"]
    ))

    booking_id = cur.lastrowid
    # SAVE MENU ITEMS
    for category, item in session["menu_items"].items():

        conn.execute("""
            INSERT INTO booking_menu_items
            (booking_id, category, item_name)
            VALUES (?, ?, ?)
        """, (booking_id, category, item))

    conn.commit()
    conn.close()
    
    for key in ["booking", "menu_items", "menu_type", "hall", "hotel"]:
        session.pop(key, None)
    flash("Booking submitted successfully!", "success")

    session["booking_completed"] = True
    return redirect(url_for("my_bookings"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login", next="profile"))
    
    conn = get_db()

    user = conn.execute(
        "SELECT username, email, ph_number FROM register WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()
    return render_template("profile.html", user=user)


@app.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        ph_number = request.form["ph_number"]
        conn.execute("""
            UPDATE register
            SET username=?, email=?, ph_number=?
            WHERE id=?
        """, (username, email, ph_number, session["user_id"]))

        conn.commit()
        conn.close()

        flash("Profile updated successfully", "success")
        return redirect(url_for("profile"))

    user = conn.execute("""
        SELECT username, email, ph_number
        FROM register WHERE id=?
    """, (session["user_id"],)).fetchone()
    conn.close()

    return render_template("update_profile.html", user=user)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = get_db()
    if request.method == "POST":
        current = request.form["current_password"]
        new = request.form["new_password"]
        confirm = request.form["confirm_password"]

        user = conn.execute("""
            SELECT password FROM register WHERE id=?
        """, (session["user_id"],)).fetchone()

        if user["password"] != current:
            flash("Current password is incorrect", "error")
            return redirect(url_for("change_password"))

        if new != confirm:
            flash("New passwords do not match", "error")
            return redirect(url_for("change_password"))

        conn.execute("""
            UPDATE register SET password=? WHERE id=?
        """, (new, session["user_id"]))

        conn.commit()
        conn.close()
        
        flash("Password updated successfully", "success")
        return redirect(url_for("profile"))
    
    conn.close()
    return render_template("change_password.html")


@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = get_db()
    bookings = conn.execute("""
        SELECT id, hotel_name, event_date, start_time, status, payment_status, event_status
        FROM bookings
        WHERE user_id = ?
        ORDER BY event_date DESC
    """, (session["user_id"],)).fetchall()

    conn.close()
    return render_template("my_bookings.html", bookings=bookings, now=datetime.now())


@app.route("/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):
    if "user_id" not in session:
        flash("Please login first", "Warning")
        return redirect(url_for("login"))
    
    conn = get_db()
    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id=? AND user_id=?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()

        flash("Booking not found", "error")
        return redirect(url_for("my_bookings"))
    
    # cannot cancel rejected / ended
    if booking["status"] in ("rejected", "cancelled") or booking["event_status"] == "ended":
        conn.close()
        flash("Booking cannot be cancelled", "error")
        return redirect(url_for("my_bookings"))
    
    # TIME LOGIC
    event_start = datetime.strptime(
        f"{booking['event_date']} {booking['start_time']}",
        "%Y-%m-%d %H:%M"
    )
    now = datetime.now()

    # event already started
    if now >= event_start:
        conn.close()
        flash("Event already started, cancellation not allowed", "error")
        return redirect(url_for("my_bookings"))
    
    # if today, block within 3 hours
    if event_start.date() == now.date():
        if event_start - now < timedelta(hours=3):
            conn.close()
            flash("Cancellation not allowed within 3 hours of event start", "error")
            return redirect(url_for("my_bookings"))
        
    # CANCEL BOOKING
    if booking["payment_status"] == "paid" :
        conn.execute("""
            UPDATE bookings
            SET status='cancelled',
                refund_status='requested'
            WHERE id=?
        """, (booking_id,))
    else:
        conn.execute("""
            UPDATE bookings
            SET status='cancelled'
            WHERE id=?
        """, (booking_id,))

    # ADMIN NOTIFICATION
    conn.execute("""
        INSERT INTO admin_notifications (hotel_name, message, created_at)
        VALUES (?, ?, DATETIME('now'))
    """, (
        booking["hotel_name"],
        f"Booking ID {booking_id} was cancelled by guest"
    ))

    conn.commit()
    conn.close()

    flash("Booking cancelled successfully", "success")
    return redirect(url_for("my_bookings"))


@app.route("/booking/<int:booking_id>")
def booking_details(booking_id):
    if "user_id" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    
    conn = get_db()
    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id=? AND user_id=?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        flash("Booking not found", "error")
        return redirect(url_for("my_bookings"))
    menu_items = conn.execute("""
        SELECT category, item_name
        FROM booking_menu_items
        WHERE booking_id=?
    """, (booking_id,)).fetchall()

    conn.close()
    return render_template("booking_details.html", booking=booking, menu_items=menu_items)


@app.route("/payment/<int:booking_id>")
def payment(booking_id):
    conn = get_db()

    conn.execute("""
        UPDATE bookings SET payment_status='paid', status='paid'
        WHERE id=? AND user_id=?
    """, (booking_id, session["user_id"]))

    conn.commit()
    conn.close()

    flash("Payment successful", "success")
    return redirect(url_for("my_bookings"))


@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    
    conn = get_db()

    notifications = conn.execute("""
        SELECT * FROM admin_notifications
        WHERE hotel_name=? AND seen=0
        ORDER BY created_at DESC
    """, (session["admin_hotel"],)).fetchall()

    conn.close()
    return render_template("admin.html", notifications=notifications)

    
@app.route("/admin/bookings/<int:booking_id>")
def admin_booking_details(booking_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    
    source = request.args.get("source","bookings")
    
    conn = get_db()

    # Main booking + user details
    booking = conn.execute("""
        SELECT 
            b.id,
            b.hotel_name,
            b.hall_name,
            b.event_name,
            b.event_type,
            b.event_date,
            b.start_time,
            b.end_time,
            b.capacity,
            b.menu_type,
            b.status,
            b.payment_status,
            r.username,
            r.ph_number,
            r.email
        FROM bookings b
        JOIN register r ON b.user_id = r.id
        WHERE b.id = ?
          AND b.hotel_name = ?
    """, (booking_id, session["admin_hotel"])).fetchone()

    if not booking:
        conn.close()

        flash("Booking not found", "error")
        return redirect(url_for("admin_bookings"))
    
    # Menu items
    menu_items = conn.execute("""
        SELECT category, item_name
        FROM booking_menu_items
        WHERE booking_id = ?
        ORDER BY category
    """, (booking_id,)).fetchall()

    conn.close()
    return render_template("admin_booking_details.html", booking=booking, menu_items=menu_items, source=source)


@app.route("/payment/review/<int:booking_id>")
def payment_review(booking_id):
    if "user_id" not in session:
        flash("Please login first", "Warning")
        return redirect(url_for("login"))

    conn = get_db()

    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id=? AND user_id=?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found", "error")
        return redirect(url_for("my_bookings"))

    menu_items = conn.execute("""
        SELECT item_name
        FROM booking_menu_items
        WHERE booking_id=?
    """, (booking_id,)).fetchall()

    price_per_plate = MENU_PRICES[booking["hotel_name"]][booking["menu_type"]]
    total_amount = price_per_plate * booking["capacity"]

    conn.close()

    return render_template(
        "payment_review.html",
        booking=booking,
        menu_items=menu_items,
        price_per_plate=price_per_plate,
        total_amount=total_amount
    )


@app.route("/admin/bookings")
def admin_bookings():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db()
    bookings = conn.execute("""
        SELECT id, event_name, event_date, status
        FROM bookings
        WHERE hotel_name = ?
            AND status = 'pending'
        ORDER BY event_date DESC
    """, (session["admin_hotel"],)).fetchall()
    conn.close()

    return render_template("admin_bookings.html", bookings=bookings)


@app.route("/admin/accept/<int:booking_id>")
def admin_accept(booking_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    
    conn = get_db()
    conn.execute("""
        UPDATE bookings SET status='approved'
        WHERE id=? AND hotel_name=?
    """, (booking_id, session["admin_hotel"]))
    conn.commit()
    conn.close()

    flash("Booking approved", "success")
    return redirect(url_for("admin_bookings"))


@app.route("/admin/reject/<int:booking_id>")
def admin_reject(booking_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    
    conn = get_db()
    conn.execute("""
                 UPDATE bookings
                 SET status='rejected'
                 WHERE id=? AND hotel_name=?
                 """, (booking_id, session["admin_hotel"]))
    conn.commit()
    conn.close()

    flash("Booking rejected", "success")
    return redirect(url_for("admin_bookings"))


@app.route("/admin/reports", methods=["GET", "POST"])
def admin_reports():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")
    filter_type = request.form.get("filter", "all")
    today = date.today().strftime("%Y-%m-%d")

    query = """
        SELECT id, event_name, event_date, start_time, end_time, status, payment_status, event_status
        FROM bookings
        WHERE hotel_name = ?
          AND status != 'pending'
    """
    params = [session["admin_hotel"]]

    if from_date and to_date:
        query += " AND event_date BETWEEN ? AND ?"
        params.extend([from_date, to_date])

    elif filter_type == "past":
        query += " AND event_date < ?"
        params.append(today)

    elif filter_type == "today":
        query += " AND event_date = ?"
        params.append(today)

    elif filter_type == "upcoming":
        query += " AND event_date > ?"
        params.append(today)

    query += " ORDER BY event_date DESC"

    conn = get_db()
    bookings = conn.execute(query, params).fetchall()
    conn.close()
    
    now = datetime.now()

    return render_template(
        "admin_reports.html", bookings=bookings, from_date=from_date, to_date=to_date, filter_type=filter_type, today=today, now=now
    )


@app.route("/admin/end_event/<int:booking_id>")
def end_event(booking_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("""
        UPDATE bookings
        SET event_status='ended'
        WHERE id=? AND hotel_name=?
    """, (booking_id, session["admin_hotel"]))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_reports"))


@app.route("/admin/generate_bill_page/<int:booking_id>")
def generate_bill_page(booking_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db()

    booking = conn.execute("""
        SELECT b.*, r.username, r.email, r.ph_number
        FROM bookings b
        JOIN register r ON b.user_id = r.id
        WHERE b.id=? AND b.hotel_name=?
    """, (booking_id, session["admin_hotel"])).fetchone()

    existing_bill = conn.execute(
        "SELECT 1 FROM bills WHERE booking_id=?",
        (booking_id,)
    ).fetchone()

    conn.close()

    if existing_bill:
        
        return redirect(url_for("invoice", booking_id=booking_id, source="admin"))

    return render_template("generate_bill.html", booking=booking)
    

@app.route("/admin/generate_bill/<int:booking_id>", methods=["POST"])
def generate_bill(booking_id):
    conn = get_db()

    exists = conn.execute(
        "SELECT 1 FROM bills WHERE booking_id=?",
        (booking_id,)
    ).fetchone()

    if exists:
        conn.close()
        flash("Bill already generated", "Warning")
        return redirect(url_for("invoice", booking_id=booking_id))

    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id=? AND hotel_name=?
    """, (booking_id, session["admin_hotel"])).fetchone()

    price = MENU_PRICES[booking["hotel_name"]][booking["menu_type"]]
    total = price * booking["capacity"]

    conn.execute("""
        INSERT INTO bills (booking_id, total_amount, generated_on)
        VALUES (?, ?, DATE('now'))
    """, (booking_id, total))

    conn.execute("""
        UPDATE bookings SET payment_status='billed'
        WHERE id=?
    """, (booking_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("invoice", booking_id=booking_id, source="admin"))


@app.route("/invoice/<int:booking_id>")
def invoice(booking_id):
    conn = get_db()

    source = request.args.get("source")

    data = conn.execute("""
        SELECT b.*, r.username, r.email, r.ph_number, bl.total_amount, bl.generated_on
        FROM bookings b
        JOIN register r ON b.user_id = r.id
        JOIN bills bl ON bl.booking_id = b.id
        WHERE b.id=?
    """, (booking_id,)).fetchone()
  
    menu_items = conn.execute("""
                SELECT item_name
                FROM booking_menu_items
                Where booking_id=?
            """, (data["id"],)).fetchall()
    
    price_per_plate = MENU_PRICES[data["hotel_name"]][data["menu_type"]]
    
    conn.close()

    return render_template("invoice.html", bill=data, price_per_plate=price_per_plate, menu_items=menu_items, source=source)


@app.route("/logout")
def logout():
    session.clear()
    flash("👋 Logged out successfully", "success")
    return redirect(url_for("home"))


@app.template_filter('todatetime')
def todatetime(value, fmt='%Y-%m-%d %H:%M'):
    return datetime.strptime(value, fmt)


if __name__ == "__main__":
    app.run(debug=True)
