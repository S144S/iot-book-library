from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user

from app import UserManagement, app, bcrypt, db, login_manager


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        phone = request.form["phone"]
        password = request.form["password"]
        if not fname or not lname or not phone or not password:
            flash("پر کردن تمام فیلدها اجباری می باشد!!", "danger")
            return redirect(url_for('register'))
        re_password = request.form["confirm_password"]
        if password != re_password:
            flash("گذرواژه و تکرار گذرواژه یکسان نیست!", "danger")
            return redirect(url_for('register'))
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        done = db.users.add_user(phone, hashed_password, fname, lname)
        if done:
            flash("ثبت‌نام با موفقیت انجام شد!", "success")
            return redirect(url_for('login'))
        else:
            flash("خطا در ثبت‌نام، لطفا دوباره امتحان کنید.", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    return UserManagement(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]
        uid = db.users.get_user_id(phone)
        if uid == 0:
            flash(' مطمئن هستی قبلا ثبت نام کردی؟!', 'warning')
            return redirect(url_for('login'))
        user = db.users.get_user(uid)
        if bcrypt.check_password_hash(user["password"], password):
            login_user(UserManagement(uid), remember=True)
            db.users.update_user_last_login(uid)
            return redirect(url_for('home'))
        else:
            flash('رمزعبور صحیح نیست!!', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    user_info = db.users.get_user(current_user.id)
    return render_template('index.html', user_info=user_info)

@app.route('/contact')
@login_required
def contact():
    user_info = db.users.get_user(current_user.id)
    return render_template('contact.html', user_info=user_info)


@app.route('/ehda', methods=['GET', 'POST'])
@login_required
def ehda():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        book_name = request.form["name"]
        author = request.form["writer"]
        publisher = request.form["publisher"]
        subject = request.form["subject"]
        address = request.form["address"]
        description = request.form["description"]
        # TODO: Add donated book into the database
        if not book_name or not author or not publisher or not address:
            flash('افزودن نام کتاب، نویسنده، ناشر و آدرس الزامی است!!', 'danger')
        else:
            flash('فرم اهدا با موفقیت ثبت شد، بزودی با شما تماس گرفته می‌شود.', 'success')
    return render_template('ehda.html', user_info=user_info)

@app.route('/request-book', methods=['GET', 'POST'])
@login_required
def request_book():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        book_name = request.form["name"]
        author = request.form["writer"]
        publisher = request.form["publisher"]
        subject = request.form["subject"]
        description = request.form["description"]
        # TODO: Add donated book into the database
        if not book_name or not author or not publisher:
            flash('افزودن نام کتاب، نویسنده و ناشر الزامی است!!', 'danger')
        else:
            flash('فرم اهدا با موفقیت ثبت شد، بزودی با شما تماس گرفته می‌شود.', 'success')
    return render_template('book_req.html', user_info=user_info)


@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        table_id = data.get('tableId')
        table_id = int(table_id[5:])
        # TODO: Update reserved table on the db

        print(f'Reserving table: {table_id} for {date} at {time}')
        return jsonify({'message': f'میز {table_id} در تاریخ {date} و ساعت {time} رزرو شد.'})

    return render_template('reserve.html', user_info=user_info)

@app.route('/check-table', methods=['POST'])
@login_required
def check_table():
    user_info = db.users.get_user(current_user.id)
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')
    print(date, time)
    # TODO: Check table reservation status by hour and date
    table1 = True
    table2 = True
    table3 = True
    table4 = False
    return jsonify({
        'table1': table1,
        'table2': table2,
        'table3': table3,
        'table4': table4
    })

