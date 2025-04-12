from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user
import jdatetime

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

@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        national_id = str(request.form["national_id"])
        # TODO: Add donated book into the database
        if not national_id:
            flash('افزودن کد ملی الزامی است!!', 'danger')
        elif len(national_id) != 10:
            flash('کد ملی باید 10 رقم باشد!', 'danger')
        else:
            done = db.subscribed_users.add_subscribed_user(int(current_user.id), national_id)
            if done:
                flash('عضویت شما با موفقیت انجام شد.', 'success')
            else:
                flash('خطا در عضویت، لطفا دوباره امتحان کنید.', 'danger')

    return render_template('subscribe.html', user_info=user_info)

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
        if not book_name or not author or not publisher or not address:
            flash('افزودن نام کتاب، نویسنده، ناشر و آدرس الزامی است!!', 'danger')
        else:
            if db.donated_books.add_donated_book(current_user.id, book_name, author, publisher, address, subject, description):
                flash('فرم اهدا با موفقیت ثبت شد، بزودی با شما تماس گرفته می‌شود.', 'success')
            else:
                flash('خطا در ثبت اهدا، لطفا دوباره امتحان کنید.', 'danger')
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
        if not book_name or not author or not publisher:
            flash('افزودن نام کتاب، نویسنده و ناشر الزامی است!!', 'danger')
        else:
            if db.requested_books.add_requested_book(current_user.id, book_name, author, publisher, subject, description):
                flash('فرم درخواست با موفقیت ثبت شد، بزودی با شما تماس گرفته می‌شود.', 'success')
            else:
                flash('خطا در ثبت درخواست، لطفا دوباره امتحان کنید.', 'danger')
    return render_template('book_req.html', user_info=user_info)


@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        start_hour = int(time.split(" - ")[0].split(":")[0])
        table_id = data.get('tableId')
        table_id = int(table_id[5:])

        done = db.reservation.add_reservation(current_user.id, date, start_hour, table_id)
        if done:
            print(f'Reserving table: {table_id} for {date} at {time}')
            return jsonify({'message': f'میز {table_id} در تاریخ {date} و ساعت {time} رزرو شد.'})
        else:
            return jsonify({'error': "error"}), 500

    return render_template('reserve.html', user_info=user_info)

@app.route('/check-table', methods=['POST'])
@login_required
def check_table():
    user_info = db.users.get_user(current_user.id)
    data = request.get_json()
    date = data.get('date')
    time = data.get('time', '00:00 - 00:00')
    start_hour = int(time.split(" - ")[0].split(":")[0])
    tabels = db.reservation.get_table_status(date, start_hour)
    print(tabels)
    return jsonify({
        'table1': tabels.get('table1', False),
        'table2': tabels.get('table2', False),
        'table3': tabels.get('table3', False),
        'table4': tabels.get('table4', False)
    })


## HARDWARE APIs
@app.route('/get_national_ids', methods=['GET'])
def get_national_ids():
    national_ids = db.subscribed_users.get_all_national_ids()
    return jsonify({'national_ids': national_ids})


@app.route('/get_reservation', methods=['GET'])
def get_reservation():
    availability = db.reservation.get_table_availability_for_now()
    return jsonify({'availability': availability})
