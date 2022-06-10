from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime
import json

print(" * Loading access tokens...")
with open('tokens.txt', 'r') as tokenFile:
    accessTokens = tokenFile.read().split(',')
    print(" * Access tokens: " + str(accessTokens))

print(" * Loading database credentials...")
with open('db.json', 'r') as dbFile:
    data = json.loads(dbFile.read())
    mysql_host = data['host']
    mysql_port = int(data['port'])
    mysql_user = data['user']
    mysql_password = data['password']
    mysql_database = data['database']

print(" * Starting flask...")
app = Flask(__name__)


@app.route('/')
def service_version():
    return '{"service":"Bubbletill BACKEND", "version": "22.0.1"}', 200


# Login
@app.route('/pos/login', methods=['POST'])
def pos_login():
    if 'token' not in request.get_json() or 'user' not in request.get_json() \
            or 'password' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT * FROM operators WHERE id = %s"
    adr = (request.get_json()['user'],)

    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Invalid user id or password."}', 200

    if result['password'] == request.get_json()['password']:
        success = {"success": True}
        result.update(success)
        return jsonify(result), 200
    else:
        return '{"success": false, "message": "Invalid user id or password."}', 200


# Update Reg Data
@app.route('/pos/today', methods=['POST'])
def pos_today():
    if 'token' not in request.get_json() or 'reg' not in request.get_json() or 'store' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT trans FROM transactions WHERE `store` = %s AND `register` = %s AND `date` = %s ORDER BY trans DESC"
    adr = (request.get_json()['store'], request.get_json()['reg'], datetime.today().strftime('%d/%m/%y'),)
    print(adr)
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '0', 200

    return str(result['trans']), 200


# Stock
@app.route('/stock/category', methods=['POST'])
def stock_category():
    if 'token' not in request.get_json() or 'category' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT description FROM categories WHERE `id` = %s"
    adr = (request.get_json()['category'],)
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Invalid category."}', 200

    return '{"success": true, "message":"' + result['description'] + '"}', 200


@app.route('/stock/item', methods=['POST'])
def stock_item():
    if 'token' not in request.get_json() or 'category' not in request.get_json() or 'code' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT * FROM stock WHERE `category` = %s AND `code` = %s"
    adr = (request.get_json()['category'], request.get_json()['code'],)
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Invalid item."}', 200

    success = {"success": True}
    result.update(success)
    return jsonify(result), 200


# POS
@app.route('/pos/submit', methods=['POST'])
def pos_submit():
    if 'token' not in request.get_json() or 'store' not in request.get_json() \
            or 'register' not in request.get_json() or 'date' not in request.get_json() \
            or 'trans' not in request.get_json() or 'oper' not in request.get_json() \
            or 'items' not in request.get_json() or 'total' not in request.get_json() \
            or 'primary_method' not in request.get_json() or 'type' not in request.get_json() \
            or 'time' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor()

    items = json.loads(request.get_json()['items'])

    sql = "INSERT INTO `transactions` (`store`, `register`, `date`, `time`, `trans`, `type`, `oper`, `items`, `total`, `primary_method`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    adr = (
        request.get_json()['store'], request.get_json()['register'], request.get_json()['date'],
        request.get_json()['time'], request.get_json()['trans'], request.get_json()['type'],
        request.get_json()['oper'], request.get_json()['items'], request.get_json()['total'],
        request.get_json()['primary_method'],)
    cur.execute(sql, adr)

    cnx.commit()

    return '', 200


@app.route('/pos/suspend', methods=['POST'])
def pos_suspend():
    if 'token' not in request.get_json() or 'store' not in request.get_json() \
            or 'date' not in request.get_json() or 'reg' not in request.get_json() \
            or 'oper' not in request.get_json() or 'items' not in request.get_json() \
            or 'total' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor()

    sql = "INSERT INTO `suspended` (`store`, `date`, `reg`, `oper`, `items`, `total`) VALUES (%s, %s, %s, %s, %s, %s)"
    adr = (
        request.get_json()['store'], request.get_json()['date'], request.get_json()['reg'], request.get_json()['oper'],
        request.get_json()['items'], request.get_json()['total'],)
    cur.execute(sql, adr)

    cnx.commit()

    return '', 200


@app.route('/pos/resume', methods=['POST'])
def pos_resume():
    if 'token' not in request.get_json() or 'usid' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT `items` FROM suspended WHERE `usid` = %s"
    adr = (request.get_json()['usid'],)
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Invalid USID."}', 200

    success = {"success": True}
    result.update(success)

    sql = "DELETE FROM suspended WHERE `usid` = %s"
    adr = (request.get_json()['usid'],)
    cur.execute(sql, adr)

    cnx.commit()

    return result['items'], 200


@app.route('/pos/listsuspended', methods=['POST'])
def pos_listsuspended():
    if 'token' not in request.get_json() or 'store' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT `usid`, `date`, `reg`, `oper`, `total` FROM suspended WHERE `store` = %s"
    adr = (request.get_json()['store'],)
    cur.execute(sql, adr)

    result = cur.fetchall()
    if result is None:
        return '{"success": false, "message":"No transactions found."}', 200

    return jsonify(result), 200


@app.route('/pos/getfloat', methods=['POST'])
def pos_getfloat():
    if 'token' not in request.get_json() or 'store' not in request.get_json() \
            or 'reg' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT * FROM floats WHERE `store` = %s AND `reg` = %s"
    adr = (request.get_json()['store'], request.get_json()['reg'],)
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Potential float not found"}', 200

    return jsonify(result), 200


# Back office
@app.route('/bo/listoperators', methods=['POST'])
def bo_listoperators():
    if 'token' not in request.get_json() or 'store' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT `id`, `name`, `manager` FROM operators WHERE `managing_store` = %s"
    adr = (request.get_json()['store'],)
    cur.execute(sql, adr)

    result = cur.fetchall()
    if result is None:
        return '{"success": false, "message":"No operators found."}', 200

    return jsonify(result), 200


@app.route('/bo/listtransactions', methods=['POST'])
def bo_listtransactions():
    if 'token' not in request.get_json() or 'store' not in request.get_json() \
            or 'startDate' not in request.get_json() or 'endDate' not in request.get_json() \
            or 'startTime' not in request.get_json() or 'endTime' not in request.get_json() \
            or 'register' not in request.get_json() or 'operator' not in request.get_json() \
            or 'startTotal' not in request.get_json() or 'endTotal' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT * FROM `transactions` WHERE `store` = %s AND `date` BETWEEN %s AND %s and `time` BETWEEN %s and %s AND `total` BETWEEN %s and %s"
    adr = (request.get_json()['store'], request.get_json()['startDate'], request.get_json()['endDate'],
           request.get_json()['startTime'], request.get_json()['endTime'], request.get_json()['startTotal'],
           request.get_json()['endTotal'],)

    if request.get_json()['register'] != "":
        sql += " AND `register` = %s"
        adr += request.get_json()['register'],
    else:
        sql += " AND `register` IS NOT NULL"

    if request.get_json()['operator'] != "":
        sql += " AND `oper` = %s"
        adr += request.get_json()['operator'],
    else:
        sql += " AND `oper` IS NOT NULL"

    cur.execute(sql, adr)

    result = cur.fetchall()
    if result is None:
        return '{"success": false, "message":"No transactions found."}', 200

    return jsonify(result), 200


@app.route('/bo/gettrans', methods=['POST'])
def bo_gettrans():
    if 'token' not in request.get_json() or 'store' not in request.get_json() \
            or 'register' not in request.get_json() or 'trans' not in request.get_json() \
            or 'date' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor(dictionary=True)

    sql = "SELECT `items` FROM transactions WHERE `store` = %s AND `register` = %s AND `trans` = %s AND `date` = %s"
    adr = (request.get_json()['store'], request.get_json()['register'], request.get_json()['trans'],
           request.get_json()['date'],)
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Transaction not found"}', 200

    return jsonify(result), 200


@app.route('/bo/postvoid', methods=['POST'])
def bo_postvoid():
    if 'token' not in request.get_json() or 'utid' not in request.get_json() \
            or 'items' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    if request.get_json()['token'] not in accessTokens:
        return '{"success": false, "message":"Invalid access token."}', 403

    cnx = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cur = cnx.cursor()

    sql = "UPDATE `transactions` SET `type` = %s, `items` = %s WHERE `utid` = %s"
    adr = ("VOID", request.get_json()['items'], request.get_json()['utid'],)
    cur.execute(sql, adr)

    cnx.commit()

    return 'Success', 200

if __name__ == '__main__':
    app.run()
