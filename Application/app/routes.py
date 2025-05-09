from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user
import jdatetime
import datetime

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

@app.route('/about')
@login_required
def about():
    user_info = db.users.get_user(current_user.id)
    return render_template('about.html', user_info=user_info)

@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        national_id = str(request.form["national_id"])
        if not national_id:
            flash('افزودن کد ملی الزامی است!!', 'danger')
        elif len(national_id) != 10:
            flash('کد ملی باید 10 رقم باشد!', 'danger')
        else:
            done = db.subscribed_users.add_subscribed_user(int(current_user.id), national_id)
            if done:
                flash('عضویت شما با موفقیت انجام شد.', 'success')
            else:
                flash('شما قبلا عضو کتابخانه شده اید!', 'danger')

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
    books = db.requested_books.get_all_requested_books()
    result = []
    for book_id, book_info in books.items():
        donater = db.users.get_user(book_info['user_id'])
        fname = donater.get('fname', '')
        lname = donater.get('lname', '')
        full_name = fname + ' ' + lname
        result.append({
            'full_name': full_name,
            'book_name': book_info.get('name', ''),
            'author': book_info.get('author', ''),
            'publisher': book_info.get('publisher', '')
        })
    return render_template('ehda.html', user_info=user_info, requested_books=result)

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
    return jsonify({
        'table1': tabels.get('table1', False),
        'table2': tabels.get('table2', False),
        'table3': tabels.get('table3', False),
        'table4': tabels.get('table4', False)
    })

@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        book_name = request.form["name"]
        author = request.form["writer"]
        publisher = request.form["publisher"]
        price = request.form["price"]
        uid = request.form["uid"]
        row = request.form["row"]
        shelf = request.form["shelf"]
        if not book_name or not author or not publisher or not row or not uid or not shelf or not price:
            flash('وارد کردن همه اطلاعات اجباری است!!', 'danger')
        else:
            if not price.isdigit() or float(price) < 100:
                flash('قیمت وارد شده منطقی نیست!', 'warning')
            else:
                price = float(price)
                location = str(row) + ',' + str(shelf)
                if db.books.add_book(uid, book_name, author, publisher, price, location):
                    flash('فرم اهدا با موفقیت ثبت شد، بزودی با شما تماس گرفته می‌شود.', 'success')
                else:
                    flash('خطا در ثبت اهدا، لطفا دوباره امتحان کنید.', 'danger')
    books = db.books.get_all_books()
    return render_template('books.html', user_info=user_info, books=books)

@app.route('/list-ehda')
@login_required
def list_ehda():
    user_info = db.users.get_user(current_user.id)
    books = db.donated_books.get_all_donated_books()
    result = []
    for book_id, book_info in books.items():
        donater = db.users.get_user(book_info['user_id'])
        fname = donater.get('fname', '')
        lname = donater.get('lname', '')
        full_name = fname + ' ' + lname
        result.append({
            'full_name': full_name,
            'book_name': book_info.get('name', ''),
            'author': book_info.get('author', ''),
            'publisher': book_info.get('publisher', '')
        })

    return render_template('list_ehda.html', user_info=user_info, books=result)

@app.route('/list-request')
@login_required
def list_request():
    user_info = db.users.get_user(current_user.id)
    books = db.requested_books.get_all_requested_books()
    result = []
    for book_id, book_info in books.items():
        donater = db.users.get_user(book_info['user_id'])
        fname = donater.get('fname', '')
        lname = donater.get('lname', '')
        full_name = fname + ' ' + lname
        result.append({
            'full_name': full_name,
            'book_name': book_info.get('name', ''),
            'author': book_info.get('author', ''),
            'publisher': book_info.get('publisher', '')
        })
    return render_template('list_request.html', user_info=user_info, books=result)

@app.route('/members')
@login_required
def members():
    user_info = db.users.get_user(current_user.id)
    members = db.subscribed_users.get_all_subscribers()
    result = []
    for member in members:
        user = db.users.get_user(member['user_id'])
        if user:
            result.append({
                'fname': user.get('fname', ''),
                'lname': user.get('lname', ''),
                'national_id': member.get('national_id', ''),
                'phone': user.get('phone', ''),
                'is_active': user.get('is_active', False)
            })
    return render_template('members.html', user_info=user_info, members=result)

@app.route('/rent')
@login_required
def rent():
    user_info = db.users.get_user(current_user.id)
    rents = db.rent.get_all_rents()
    result = []
    for rent in rents:
        info = {}
        user = db.users.get_user(rent['user_id'])
        book = db.books.get_book_by_id(rent['book_id'])
        if user and book:
            info['fname'] = user.get('fname', '')
            info['lname'] = user.get('lname', '')
            info['phone'] = user.get('phone', '')
            info['national_id'] = db.subscribed_users.get_subscriber_by_user_id(rent['user_id']).get('national_id', '')
            info['book_name'] = book.get('name', '')
            gdate = rent.get('due_date', '')
            year, month, day = map(int, gdate.split('-'))
            gregorian_date = datetime.date(year, month, day)
            jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
            info['due_date'] = f"{jalali_date.year}/{jalali_date.month:02}/{jalali_date.day:02}"
            info['is_return'] = rent.get('is_return', False)
            result.append(info)
    return render_template('rent_list.html', user_info=user_info, items=result)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    books = []
    user_info = db.users.get_user(current_user.id)
    if request.method == "POST":
        book_name = request.form["name"].strip()
        author = request.form["writer"].strip()
        publisher = request.form["publisher"].strip()
        if not book_name and not author and not publisher:
            flash('وارد کردن حداقل یک فیلد اجباری است!!', 'danger')
        else:
            if book_name:
                books.append(db.books.get_book_by_name(book_name))
            if author:
                books.append(db.books.get_book_by_author(author))
            if publisher:
                books.append(db.books.get_book_by_publisher(publisher))
    return render_template('search.html', user_info=user_info, books=books)


## HARDWARE APIs
@app.route('/get_national_ids', methods=['GET'])
def get_national_ids():
    national_ids = db.subscribed_users.get_all_national_ids()
    return jsonify({'national_ids': national_ids})


@app.route('/get_reservation', methods=['GET'])
def get_reservation():
    today = jdatetime.datetime.now().togregorian().date()
    hour = datetime.datetime.now().hour
    availability = db.reservation.get_table_availability_for_now()
    return jsonify({'today': today, 'hour': hour, 'availability': availability})


@app.route('/add_rent', methods=['POST'])
def add_rent():
    data = request.get_json()
    nid = data.get('nid')
    buid = data.get('buid')
    print(nid, buid)
    if not nid or not buid:
        return jsonify({'error': 'nid and buid are required'}), 400
    
    user_id = db.subscribed_users.get_user_id_by_national_id(nid)
    book_id = db.books.get_book_by_uid(buid).get('id')
    done = db.rent.add_rent(user_id, book_id)
    if done:
        return jsonify({'stat': True}), 200
    else:
        return jsonify({'stat': False, 'error': 'Failed to add rent'}), 400

@app.route("/del-rent", methods=["POST"])
def del_rent():
    national_id = request.form.get("national_id")
    done = db.rent.delete_rents_by_national_id(str(national_id))
    if done:
        flash('تغییرات با موفقیت انجام شد', 'success')
    else:
        flash('خطایی در سمت سرور رخ داده است! بعدا تلاش کنید!', 'danger')
    return redirect("/rent")