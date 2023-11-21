from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, time, sqlite3
app = FastAPI()
db_conexions = sqlite3.connect('./pay2ads.db', 1000)
db = db_conexions.cursor()

#   add midwares
app.add_middleware(
    CORSMiddleware,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
    allow_origins=['*']
)

# create users table
db.execute("""
    CREATE TABLE IF NOT EXISTS users 
    (
        id INTEGER PRIMARY_KEY AUTO_INCREMENT, 
        username TEXT, email TEXT, reference_link TEXT, my_reference_link TEXT,
        balance TEXT, reference_bonus TEXT, clicks TEXT,
        reference_count TEXT, password TEXT, created_at TEXT
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS users_marketing 
    (
        id TEXT, username TEXT, link TEXT, posted_at TEXT
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS users_payment_forms 
    (
        id TEXT, username TEXT, back_name TEXT, iban TEXT, number TEXT, valor TEXT, created_at TEXT
    )
""")

class DBModuls:
    # create find All methodes
    def findAll (self, query):
        db.execute(f"SELECT * FROM {query}")
        result = db.fetchall()
        column = [desc[0] for desc in db.description]
        converts_to_json = [dict(zip(column, row)) for row in result]
        return converts_to_json

















# ============================ post methods =============================================
db_moduls = DBModuls()


@app.get('/api')
async def api(req: Request):
    return {"sms": "api is building..."}

# router to create new user accounts
@app.post('/app_pay2ads_registe_users')
async def app_pay2ads_registe_users (req: Request):
    res = await req.json()
    refernce_link = res['reference_link']
    user_email = res['email']

    res_1 = db_moduls.findAll(f"users WHERE my_reference_link='{refernce_link}'")
    res_2 = db_moduls.findAll(f"users WHERE email='{user_email}' ")
    if len(res_1) == 0: return {"sms": "invalid-refer"}
    if len(res_2) > 0: return {"sms": "found-id"}

    refer_data = res_1[0]
    my_referes = int(refer_data['reference_count'])
    reference_bonus = int(refer_data['reference_bonus'])
    balance = int(refer_data['balance'])
    refere_email = refer_data['email']
    update_balance = balance + 10
    update_referes = my_referes + 1
    update_refere_bonus = reference_bonus + 10

    # update referes accounts
    db.execute(f""" 
            UPDATE users SET balance='{update_balance}', reference_bonus='{update_refere_bonus}',
            reference_count='{update_referes}' WHERE email='{refere_email}'
    """)
    time.sleep(2)
    #creating a new user in the table
    db.execute(f"""INSERT INTO users 
    (
        username, email, reference_link, my_reference_link,
        balance, reference_bonus, clicks, reference_count, password, created_at
    )
    VALUES(
        '{res['username']}', '{res['email']}','{res['reference_link']}', '{res['my_refere_link']}',
        '{res['balance']}', '{res['reference_bonus']}', '{res['clicks']}','{res['reference_count']}',
        '{res['password']}','{res['created_at']}'
    )
    """)
    db_conexions.commit()
    payload = {
        "credential": {"id": res['my_refere_link']},
    }
    return {"sms": payload}
# router to create new user accounts
@app.post('/app_pay2ads_auth_users_login')
async def app_pay2ads_auth_users_login(req: Request):
    res = await req.json()
    email = res['email']
    password = res['password']
    users = db_moduls.findAll(f"users WHERE email='{email}'")
    if len(users) == 0: return {"sms": "not-found"}
    user_data = users[0]
    if password != user_data['password']: return {"sms": "invalid-password"}
    payload = {
        "credential": {"id": user_data['my_reference_link']}
    }
    #token = jwt.encode(payload=payload, key="4x8detcçlksacgsjs", algorithm="HS256")
    #print(token)
    return {"sms": payload}

# ============================ post methods =============================================
# router to create new user accounts
@app.post('/app_pay2ads_get_all_data')
async def app_pay2ads_get_all_data(req: Request):
    res = await req.json()
    ids = res['id']
    data = db_moduls.findAll(f"users WHERE my_reference_link='{ids}' ")
    return {"data": data}


# app_pay2ads_update_balance_by_user
@app.post('/app_pay2ads_update_balance_by_user')
async def app_pay2ads_update_balance_by_user(req: Request):
    res = await req.json()
    ids = res['id']
    get_balance = 0.5
    user = db_moduls.findAll(f"users WHERE my_reference_link='{ids}' ")
    data = user[0]
    if data['my_reference_link'] == data['reference_link']:
        balance = float(data['balance'])
        update_balance = balance + get_balance
        db.execute(f"UPDATE users SET balance='{update_balance}' WHERE my_reference_link='{ids}' ")
        db_conexions.commit()
        return {"sms": "sucess for admin"}
    else:
        user2 = db_moduls.findAll(f"users WHERE my_reference_link='{data['reference_link']}' ")
        data2 = user2[0]
        reference_bonus = float(data2['reference_bonus'])
        refere_balance = float(data2['balance'])
        update_refere_bonus = reference_bonus + 1
        update_refere_balance = refere_balance + 1
        balance = float(data['balance'])
        update_balance = balance + get_balance

        db.execute(f"UPDATE users SET balance='{update_balance}' WHERE my_reference_link='{ids}' ")
        time.sleep(2)
        db.execute(f"""
            UPDATE users SET balance='{update_refere_balance}', reference_bonus='{update_refere_bonus}' 
            WHERE my_reference_link='{data['reference_link']}' 
        """)
        db_conexions.commit()
        return {"sms": "sucess users"}


# app_pay2ads_get_publish_ads_by_user
@app.post('/app_pay2ads_get_publish_ads_by_user')
async def app_pay2ads_get_publish_ads_by_user(req: Request):
    res = await req.json()
    ids = res['id']
    link = res['link']
    created_at = res['created_at']
    username = res['username']
    db.execute(f""" 
        INSERT INTO users_marketing (id, username, link, posted_at)
        VALUES('{ids}', '{username}', '{link}', '{created_at}')
    """)
    db_conexions.commit()
    return {"sms": res}

# app_pay2ads_get_user_rquest_payments
@app.post('/app_pay2ads_get_user_rquest_payments')
async def app_pay2ads_get_user_rquest_payments(req: Request):
    res = await req.json()
    ids = res['id']
    db.execute(f""" 
        INSERT INTO users_payment_forms 
        (id, username, back_name, iban, number, valor, created_at)
        VALUES(
            '{ids}','{res['username']}','{res['back_name']}','{res['iban']}',
            '{res['number']}','{res['valor']}','{res['created_at']}'
        )
    """)
    db_conexions.commit()
    return {"sms": "sucess"}

# app_pay2ads_update_user_password
@app.post('/app_pay2ads_update_user_password')
async def app_pay2ads_update_user_password(req: Request):
    res = await req.json()
    ids = res['id']
    password = res['password']
    db.execute(f"UPDATE users SET password='{password}' WHERE my_reference_link='{ids}' ")
    db_conexions.commit()
    return {"sms": "sucess"}

# app_pay2ads_admin_validate_publish_ads_by_user
@app.post('/app_pay2ads_admin_validate_publish_ads_by_user')
async def app_pay2ads_admin_validate_publish_ads_by_user(req: Request):
    res = await req.json()
    ids = res['id']
    get_balance = 50.0
    user = db_moduls.findAll(f"users WHERE my_reference_link='{ids}' ")
    data = user[0]
    if data['my_reference_link'] == data['reference_link']:
        balance = float(data['balance'])
        update_balance = balance + get_balance
        db.execute(f"UPDATE users SET balance='{update_balance}' WHERE my_reference_link='{ids}' ")
        db_conexions.commit()
        return {"sms": "sucess for admin"}
    else:
        user2 = db_moduls.findAll(f"users WHERE my_reference_link='{data['reference_link']}' ")
        data2 = user2[0]
        reference_bonus = float(data2['reference_bonus'])
        refere_balance = float(data2['balance'])
        update_refere_bonus = reference_bonus + 25
        update_refere_balance = refere_balance + 25
        balance = float(data['balance'])
        update_balance = balance + get_balance

        db.execute(f"UPDATE users SET balance='{update_balance}' WHERE my_reference_link='{ids}' ")
        time.sleep(2)
        db.execute(f"""
            UPDATE users SET balance='{update_refere_balance}', reference_bonus='{update_refere_bonus}' 
            WHERE my_reference_link='{data['reference_link']}' 
        """)
        
        time.sleep(3)
        db.execute(f"DELETE FROM users_marketing WHERE id='{ids}' ")

        db_conexions.commit()
        return {"sms": "sucess users"}

    

# app_pay2ads_admin_delete_user
@app.post('/app_pay2ads_admin_delete_user')
async def app_pay2ads_get_publish_ads_by_user(req: Request):
    res = await req.json()
    ids = res['id']
    db.execute(f"DELETE FROM users WHERE my_reference_link='{ids}' ")
    db_conexions.commit()
    return {"sms": "sucess"}





# app_pay2ads_adim_get_publish_ads_by_user
@app.post('/app_pay2ads_adim_get_publish_ads_by_user')
async def app_pay2ads_adim_get_publish_ads_by_user(req: Request):
    data = db_moduls.findAll(f"users_marketing")
    return {"data": data}

# app_pay2ads_adim_get_user_request_form
@app.post('/app_pay2ads_adim_get_user_request_form')
async def app_pay2ads_adim_get_user_request_form(req: Request):
    data = db_moduls.findAll(f"users_payment_forms")
    return {"data": data}


















#   creatingnew servers and port

#PORT = 5000
#HOST_NAME = '0.0.0.0'

#uvicorn.run(app, host=HOST_NAME,port=PORT)