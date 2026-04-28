#!/usr/bin/env python3
import mysql.connector
import json

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mysql"
    )
    conn.close()
    print(json.dumps({"database": "mysql", "status": "ok"}))
except Exception as e:
    print(json.dumps({"database": "mysql", "status": "error", "msg": str(e)}))