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

    sql = "SELECT trans FROM transactions WHERE `store` = %s AND `register` = %s AND `date` = %s"
    adr = (request.get_json()['store'], request.get_json()['reg'], datetime.today().strftime('%Y-%m-%d'),)
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
    adr = (request.get_json()['category'], request.get_json()['code'], )
    cur.execute(sql, adr)

    result = cur.fetchone()
    if result is None:
        return '{"success": false, "message":"Invalid item."}', 200

    success = {"success": True}
    result.update(success)
    return jsonify(result), 200

# POS
@app.route('/pos/suspend', methods=['POST'])
def pos_suspend():
    if 'token' not in request.get_json() or 'store' not in request.get_json() \
            or 'date' not in request.get_json() or 'reg' not in request.get_json() \
            or 'oper' not in request.get_json() or 'items' not in request.get_json():
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

    sql = "INSERT INTO `suspended` (`store`, `date`, `reg`, `oper`, `items`) VALUES (%s, %s, %s, %s, %s)"
    adr = (request.get_json()['store'], request.get_json()['date'], request.get_json()['reg'], request.get_json()['oper'], request.get_json()['items'],)
    cur.execute(sql, adr)

    cnx.commit()

    return '', 200


if __name__ == '__main__':
    app.run()
