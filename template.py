from bottle import run, route, template, get, request, install
import sqlite3, inspect
from bottle_sqlite import SQLitePlugin
from zoneinfo import ZoneInfo
import locale
from datetime import datetime, timedelta
import random
import string

@route("/")
def login():
    return template('index')

# フォーム入力結果ページ
@route("/menu_user", method = 'GET')
def do_login():
    ID = request.query.get('email_ID')
    pass_word = request.query.get('pass_word')

    # ユーザー情報をuserテーブルから抽出する
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    customer_info = cursor.execute('SELECT email_ID, pass_word FROM user')
    user_id_pass = dict(customer_info.fetchall())

    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    staff_info = cursor.execute('SELECT staff_ID, pass_word FROM staff')
    staff_id_pass = dict(staff_info.fetchall())

    if ID in user_id_pass.keys() and pass_word == user_id_pass[ID]:
        return template('menu_user')
    elif ID in staff_id_pass.keys() and pass_word == staff_id_pass[ID]:
        return template('menu_cafe')
    else:
        return '''<p>ログインできませんでした。</p><br>
                  <a href="/" >ログイン画面に戻る</a>
                  <a href="/sign_up">新規会員登録する</a>
                '''

@route("/sign_up")
def sing_up():
    return template('sign_up')

@route("/sign_up_complete", method='POST')
def sign_up_complete():
    user_name = request.forms.getunicode('user_name')
    email_ID = request.forms.getunicode('email_ID')
    pass_word = request.forms.getunicode('pass_word')
    birth_year = request.forms.getunicode('birth_year')
    birth_month = request.forms.getunicode('birth_month')
    birth_day = request.forms.getunicode('birth_day')

    #会員登録時刻を追加する
    registered_datetime = datetime.now()

    db = sqlite3.connect("cafe_db.db")
    cursor_preorder = db.cursor()
    cursor_preorder.execute('INSERT INTO user (user_name, email_ID, pass_word, birth_year, birth_month, birth_day, registered_datetime) VALUES(?, ?, ?, ?, ?, ?, ?)', [user_name, email_ID, pass_word, birth_year, birth_month, birth_day, registered_datetime])
    db.commit()
    db.close()

    return template('sign_up_complete')

@route("/order_take_out")
def order_take_out():
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    rows = cursor.execute('SELECT name, price, sort FROM items')
    menu = rows.fetchall()

    return template('order_take_out', menu=menu)

@route('/takeout_order_complete', method='POST')
def complete_takeout_order():
    customer_name = request.forms.getunicode('customer_name')
    note = request.forms.getunicode('note')
    month = request.forms.getunicode('month')
    day = request.forms.getunicode('day')
    hour = request.forms.getunicode('hour')
    minite = request.forms.get('minite')

    # 予約番号生成
    LETTERS = (string.ascii_letters + string.digits)
    random_letters = random.choices(LETTERS, k=5)
    random_string = ''.join(random_letters)
    reservation_code = random_string

    #事前注文の内容を抽出
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    rows = cursor.execute('SELECT name, price, sort FROM items')
    menu = rows.fetchall()
    #menu_list と quantity_list をタプルのリストにしてSQLに渡す。
    menu_list = []
    for i in menu:
        menu_list.append(i[0])

    quantity_list = []
    for j in range(len(menu)):
        quantity = request.forms.get(f'quantity{j}')
        quantity_list.append(quantity)

    preorder_tuple = list(zip(menu_list, quantity_list))
    #zip関数はtupleでしか返してくれないので、listに変換する↓
    preorder_list = []
    for i in preorder_tuple:
        preorder_list.append(list(i))

    #注文ありのメニュー品目のみ抽出する
    preorder_items = []
    for item in preorder_list:
        if item[1] >= "1":
            preorder_items.append(item)

    #予約番号ありの事前注文リストにする
    preorder_with_reservation_code = []
    for i in preorder_items:
        i.append(reservation_code)
        preorder_with_reservation_code.append(i)

    #予約完了した時間を抽出
    order_complete_time = datetime.now()

    db = sqlite3.connect("cafe_db.db")
    cursor_preorder = db.cursor()
    cursor_preorder.executemany('INSERT INTO takeout_order (name, quantity, reservation_code) VALUES(?, ?, ?)', preorder_with_reservation_code)
    db.commit()
    db.close()

    # テイクアウト情報をtakeout_infoテーブルに格納する
    db = sqlite3.connect("cafe_db.db")
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO takeout_info(customer_name, note, reservation_code, month, day, order_complete_time, hour, minite) VALUES(?,?,?,?,?,?,?,?)',
        [customer_name, note, reservation_code, month, day, order_complete_time, hour, minite])
    db.commit()
    db.close()

    return template('takeout_order_complete', customer_name=customer_name, note=note, preorder_items = preorder_items,
                    month = month, day = day, hour = hour, minite = minite)

@route('/reserve/<date>/<time>')
def reserve(date, time):
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    rows = cursor.execute('SELECT name, price, sort FROM items')
    menu = rows.fetchall()

    return template('reserve', menu = menu, date = date, time = time)

@route('/confirm_reserve/<date>/<time>', method='POST')
def confirm_reservation(date, time):
    customer_name = request.forms.getunicode('customer_name')
    number_of_customer = request.forms.get('number_of_customer')
    duration = request.forms.get('duration')
    note = request.forms.getunicode('note')
    email = request.forms.getunicode('email')

    # 予約番号生成
    LETTERS = (string.ascii_letters + string.digits)
    random_letters = random.choices(LETTERS, k=5)
    random_string = ''.join(random_letters)
    reservation_code = random_string

    #事前注文の内容を抽出
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    rows = cursor.execute('SELECT name, price, sort FROM items')
    menu = rows.fetchall()
    #menu_list と quantity_list をタプルのリストにしてSQLに渡す。
    menu_list = []
    for i in menu:
        menu_list.append(i[0])

    quantity_list = []
    for j in range(len(menu)):
        quantity = request.forms.get(f'quantity{j}')
        quantity_list.append(quantity)

    preorder_tuple = list(zip(menu_list, quantity_list))
    #zip関数はtupleでしか返してくれないので、listに変換する↓
    preorder_list = []
    for i in preorder_tuple:
        preorder_list.append(list(i))

    #注文ありのメニュー品目のみ抽出する
    preorder_items = []
    for item in preorder_list:
        if item[1] >= "1":
            preorder_items.append(item)

    #予約番号ありの事前注文リストにする
    preorder_with_reservation_code = []
    for i in preorder_items:
        i.append(reservation_code)
        preorder_with_reservation_code.append(i)

    #予約完了した時間を抽出
    order_complete_time = datetime.now()

    db = sqlite3.connect("cafe_db.db")
    cursor_preorder = db.cursor()
    cursor_preorder.executemany('INSERT INTO preorder (name, quantity, reservation_code) VALUES(?, ?, ?)', preorder_with_reservation_code)
    db.commit()
    db.close()

    # 予約情報をreservations.dbに格納する
    db = sqlite3.connect("reservations.db")
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO reservations(datetime, time, customer_name,number_of_customer,duration,remarks, reservation_code, order_complete_time, email) VALUES(?,?,?,?,?,?,?,?,?)',
        [date, time, customer_name, number_of_customer, duration, note, reservation_code, order_complete_time, email])
    db.commit()
    db.close()

    # duration = 2（予約時間が2時間）の場合、予約を2つ作る分岐
    if duration == "2":
        time = int(time) +1
        db = sqlite3.connect("reservations.db")
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO reservations(datetime, time, customer_name,number_of_customer,remarks, reservation_code, order_complete_time) VALUES(?,?,?,?,?,?,?)',
            [date, time, customer_name, number_of_customer, note, reservation_code, order_complete_time])
        db.commit()
        db.close()

    return template('confirm_reserve', customer_name=customer_name, number_of_customer=number_of_customer,
                    duration=duration, note=note, email=email, preorder_items = preorder_items, date = date, time = time, reservation_code = reservation_code)

@route('/weekly_vacancy/<times>')
def weekly_vacancy(times):
    #現在の日時を取得
    times = int(times)
    now = datetime.now() + timedelta(weeks=times)
    # (1)今週の日にちと (2)曜日を抽出し、リストに格納
    this_week = []  # (1)datetime型
    this_week_str = []  # str型で格納。後ほど使用する
    day_of_week = []  # (2)今週の曜日を抽出し、リストに格納
    locale.setlocale(locale.LC_ALL, '')  # 曜日作成（曜日を日本語で取得）

    for i in range(0, 7):
        t = now + timedelta(days=i)
        t = t.date()
        this_week.append(t.strftime('%m/%d'))
        day_of_week.append(t.strftime('%a'))
        this_week_str.append(str(t))

    #まず全予約を抽出する
    db = sqlite3.connect(
        "reservations.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT datetime, time, number_of_customer FROM reservations '''
    c = db.execute(sql).fetchall()

    def make_dict(time):
        #今週の予約を1つ1つ抽出
        reservations_this_week = []
        for i in c:
            for j in this_week_str:
                if i[0] == j and i[1] == time:
                    reservations_this_week.append(i)
        # print(ten_reservations_this_week)

        # 一旦、今週の予約席数を0にし、辞書を作成
        dict = {}
        for i in this_week_str:
            dict[i] = 0

        # 今週の予約席数を計算し、dictに格納する
        for i in dict.keys():
            for k in reservations_this_week:
                if i == k[0]:
                    dict[i] += k[2]

        return dict

    #10時～16時のdictを作成する
    dict_list =[]
    for i in range(10, 17):
        dict_list.append(make_dict(i))

    # weekly2.htmlの時間表示用のリスト
    hours = list(range(10, 17))

    times = times + 1

    return template('weekly2', this_week= this_week, day_of_week = day_of_week, dict_list = dict_list, hours = hours, times = times)

@route('/weekly_vacancy_for_cafe')
def weekly_vacancy_for_cafe():
    #現在の日時を取得
    now = datetime.now()
    # (1)今週の日にちと (2)曜日を抽出し、リストに格納
    this_week = []  # (1)datetime型
    this_week_str = []  # str型で格納。後ほど使用する
    day_of_week = []  # (2)今週の曜日を抽出し、リストに格納
    locale.setlocale(locale.LC_ALL, '')  # 曜日作成（曜日を日本語で取得）

    for i in range(0, 7):
        t = now + timedelta(days=i)
        t = t.date()
        this_week.append(t.strftime('%m/%d'))
        day_of_week.append(t.strftime('%a'))
        this_week_str.append(str(t))

    #まず全予約を抽出する
    db = sqlite3.connect(
        "reservations.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT datetime, time, number_of_customer FROM reservations '''
    c = db.execute(sql).fetchall()

    def make_dict(time):
        #今週の予約を1つ1つ抽出
        reservations_this_week = []
        for i in c:
            for j in this_week_str:
                if i[0] == j and i[1] == time:
                    reservations_this_week.append(i)
        # print(ten_reservations_this_week)

        # 一旦、今週の予約席数を0にし、辞書を作成
        dict = {}
        for i in this_week_str:
            dict[i] = 0

        # 今週の予約席数を計算し、dictに格納する
        for i in dict.keys():
            for k in reservations_this_week:
                if i == k[0]:
                    dict[i] += k[2]

        return dict

    #10時～16時のdictを作成する
    dict_list =[]
    for i in range(10, 17):
        dict_list.append(make_dict(i))

    # weekly2.htmlの時間表示用のリスト
    hours = list(range(10, 17))

    return template('weekly_vacancy_for_cafe', this_week= this_week, day_of_week = day_of_week, dict_list = dict_list, hours = hours)

@route('/reserve_for_cafe/<date>/<time>')
def reserve_for_cafe(date, time):
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    rows = cursor.execute('SELECT name, price, sort FROM items')
    menu = rows.fetchall()
    return template('reserve_for_cafe', menu = menu, date = date, time = time)

@route('/complete_reservation_for_cafe/<date>/<time>', method='POST')
def complete_reservation_for_cafe(date, time):
    customer_name = request.forms.getunicode('customer_name')
    number_of_customer = request.forms.get('number_of_customer')
    duration = request.forms.get('duration')
    note = request.forms.getunicode('note')

    # 予約番号生成
    LETTERS = (string.ascii_letters + string.digits)
    random_letters = random.choices(LETTERS, k=5)
    random_string = ''.join(random_letters)
    reservation_code = random_string

    #事前注文の内容を抽出
    con = sqlite3.connect("cafe_db.db")
    cursor = con.cursor()
    rows = cursor.execute('SELECT name, price, sort FROM items')
    menu = rows.fetchall()
    #menu_list と quantity_list をタプルのリストにしてSQLに渡す。
    menu_list = []
    for i in menu:
        menu_list.append(i[0])

    quantity_list = []
    for j in range(len(menu)):
        quantity = request.forms.get(f'quantity{j}')
        quantity_list.append(quantity)

    preorder_tuple = list(zip(menu_list, quantity_list))
    #zip関数はtupleでしか返してくれないので、listに変換する↓
    preorder_list = []
    for i in preorder_tuple:
        preorder_list.append(list(i))

    #注文ありのメニュー品目のみ抽出する
    preorder_items = []
    for item in preorder_list:
        if item[1] >= "1":
            preorder_items.append(item)

    #予約番号ありの事前注文リストにする
    preorder_with_reservation_code = []
    for i in preorder_items:
        i.append(reservation_code)
        preorder_with_reservation_code.append(i)

    #予約完了した時間を抽出
    order_complete_time = datetime.now()

    db = sqlite3.connect("cafe_db.db")
    cursor_preorder = db.cursor()
    cursor_preorder.executemany('INSERT INTO preorder (name, quantity, reservation_code) VALUES(?, ?, ?)', preorder_with_reservation_code)
    db.commit()
    db.close()

    # 予約情報をreservations.dbに格納する
    db = sqlite3.connect("reservations.db")
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO reservations(datetime, time, customer_name,number_of_customer,duration,remarks, reservation_code, order_complete_time, is_event) VALUES(?,?,?,?,?,?,?,?,?)',
        [date, time, customer_name, number_of_customer, duration, note, reservation_code, order_complete_time, 1])
    db.commit()
    db.close()

    # duration >= 2（予約時間が2時間）の場合、予約を時間分作る
    duration = int(duration)
    time = int(time)
    if duration >= 2:
        for i in range(duration-1):
            time += 1
            db = sqlite3.connect("reservations.db")
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO reservations(datetime, time, customer_name,number_of_customer,remarks, reservation_code, order_complete_time, is_event) VALUES(?,?,?,?,?,?,?,?)',
                [date, time, customer_name, number_of_customer, note, reservation_code, order_complete_time, 1])
            db.commit()
            db.close()

    return template('complete_reservation_for_cafe', customer_name=customer_name, number_of_customer=number_of_customer,
                    duration=duration, note=note, preorder_items = preorder_items, date = date, time = time, reservation_code = reservation_code)

@route("/inquiry", method = 'GET')
#予約情報を表示する
def inquiry():
    #予約情報をDBから抽出
    reservation_code = request.query.get('input_reservation_code')
    #reservationDBに接続
    db = sqlite3.connect(
        "reservations.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT reservation_code, customer_name, datetime, time, number_of_customer, duration FROM reservations '''
    all_reservations = db.execute(sql).fetchall()
    print(all_reservations)
    inquired_reservation = []
    for one in all_reservations:
        if one[5] != '' and reservation_code == one[0]:
            inquired_reservation= list(one)

    #事前注文を表示
    # preorderDBに接続
    db = sqlite3.connect(
        "cafe_db.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT reservation_code, name, quantity FROM preorder '''
    all_preorders = db.execute(sql).fetchall()
    db.close()

    inquired_preorders = []
    for one in all_preorders:
        if reservation_code == one[0]:
            inquired_preorders.append(one)

    #テイクアウト情報の照会
    db = sqlite3.connect(
        "cafe_db.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT reservation_code, month, day, hour, minite, note FROM takeout_info '''
    all_takeout = db.execute(sql).fetchall()
    db.close()

    inquired_all_takeout_info = []
    for one in all_takeout:
        if reservation_code == one[0]:
            inquired_all_takeout_info = list(one)

    #テイクアウトの注文詳細
    db = sqlite3.connect(
        "cafe_db.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT reservation_code, name, quantity FROM takeout_order '''
    all_takeout_order = db.execute(sql).fetchall()
    db.close()

    inquired_takeout_order = []
    for one in all_takeout_order:
        if reservation_code == one[0]:
            inquired_takeout_order.append(one)

    #現在の席状況を表示
    now = datetime.now()  #今の時刻 '2024-03-21 10:00:00'形式

    this_week = []  # (1)datetime型
    this_week_str = []  # str型で格納。後ほど使用する
    day_of_week = []  # (2)今週の曜日を抽出し、リストに格納
    locale.setlocale(locale.LC_ALL, '')  # 曜日作成（曜日を日本語で取得）

    for i in range(0, 7):
        t = now + timedelta(days=i)
        t = t.date()
        this_week.append(t.strftime('%m/%d'))
        day_of_week.append(t.strftime('%a'))
        this_week_str.append(str(t))

    # まず全予約を抽出する
    db = sqlite3.connect(
        "reservations.db",
        isolation_level=None,
    )
    cur = db.cursor()
    sql = ''' SELECT datetime, time, number_of_customer FROM reservations '''
    c = db.execute(sql).fetchall()

    def make_dict(time):
        # 今週の予約を1つ1つ抽出
        reservations_this_week = []
        for i in c:
            for j in this_week_str:
                if i[0] == j and i[1] == time:
                    reservations_this_week.append(i)
        # print(ten_reservations_this_week)

        # 一旦、今週の予約席数を0にし、辞書を作成
        dict = {}
        for i in this_week_str:
            dict[i] = 0

        # 今週の予約席数を計算し、dictに格納する
        for i in dict.keys():
            for k in reservations_this_week:
                if i == k[0]:
                    dict[i] += k[2]
        return
    print(dict[0])

    # 10時～16時のdictを作成する
    dict_list = []
    for i in range(10, 17):
        dict_list.append(make_dict(i))

    # weekly2.htmlの時間表示用のリスト
    hours = list(range(10, 17))

    return template('inquiry', inquired_reservation = inquired_reservation, inquired_preorders = inquired_preorders,
                    inquired_all_takeout_info = inquired_all_takeout_info, inquired_takeout_order = inquired_takeout_order, reservation_code = reservation_code)

@route("/menu_cafe/<reservation_code>", method = 'POST')
def menu_cafe(reservation_code):
    db = sqlite3.connect("reservations.db")
    cursor_preorder = db.cursor()
    cursor_preorder.execute(
        'UPDATE reservations SET is_arrived = 1 WHERE reservation_code == reservation_code')
    db.commit()
    db.close()
    return template('menu_cafe')

if __name__ == "__main__":
    run(host='127.0.0.1', port=8080, reloader=True, debug=True)

