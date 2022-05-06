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


if __name__ == '__main__':
    app.run()
