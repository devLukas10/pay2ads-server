import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, time

app = FastAPI()
#   add midwares

app.add_middleware(
    CORSMiddleware,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
    allow_origins=['*']
)

# making conexions with data base
try:
    db_conexions = psycopg2.connect(
        database = "pay_to_ads", 
        user = "muana_mayele", 
        host= 'dpg-cleeshds40us73c0ivq0-a.singapore-postgres.render.com',
        password = "ZBYEArq1ubwYugrIjzr4g981j418gFqT",
        port = 5432,
        #ssl= True,
    )
    db = db_conexions.cursor()
    print("conection done...")

    # starting a table
    # create users table
    db.execute("""
            CREATE TABLE IF NOT EXISTS users 
            ( 
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
    db.execute("""
            CREATE TABLE IF NOT EXISTS users_total_pays 
            (
                id TEXT, username TEXT, back_name TEXT, iban TEXT, number TEXT, valor TEXT, status TEXT,created_at TEXT
            )
        """)
    db.execute("""
            CREATE TABLE IF NOT EXISTS refers_list 
            (
                id TEXT, username TEXT, email TEXT
            )
        """)
    db.execute("""
            CREATE TABLE IF NOT EXISTS ibonx 
            (
                id TEXT, titler TEXT, sms TEXT, icon TEXT, state TEXT, color TEXT
            )
        """)
    db.execute("""
            CREATE TABLE IF NOT EXISTS ibonx_count
            (
                id TEXT
            )
        """)
    db.execute("CREATE TABLE IF NOT EXISTS offers_click (id TEXT, dificulty TEXT ) ")
    db.execute("CREATE TABLE IF NOT EXISTS offers_ref (id TEXT, dificulty TEXT ) ")
    db.execute("CREATE TABLE IF NOT EXISTS pay_offer (id TEXT,dificulty TEXT ) ")
    db.execute("CREATE TABLE IF NOT EXISTS offfers_game (id TEXT, dificulty TEXT ) ")
        
    db_conexions.commit()
#================================================================================
    # convert data to json files
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

    def update_offers(self, types, datas):
        user_id = datas["id"]
        # update offers clicks
        if types == "offers_click":
            user_data = db_moduls.findAll(f"offers_click WHERE id='{user_id}' ")
            dificulty = int(user_data["dificulty"]) + int(datas["dificulty"])
            db.execute(f"UPDATE offers_click SET dificulty='{dificulty}' WHERE id='{user_id}' ")
            db_conexions.commit()
        # update offers game
        if types == "offfers_game":
            user_data = db_moduls.findAll(f"offfers_game WHERE id='{user_id}' ")
            dificulty = int(user_data["dificulty"]) + int(datas["dificulty"])
            db.execute(f"UPDATE offfers_game SET dificulty='{dificulty}' WHERE id='{user_id}' ")
            db_conexions.commit()
        #update offers games
        if types == "pay_offer":
            user_data = db_moduls.findAll(f"pay_offer WHERE id='{user_id}' ")
            db.execute(f"UPDATE offers_click SET dificulty='none' WHERE id='{user_id}' ")
            db_conexions.commit()


    @app.get('/')
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
        db_conexions.commit()
        time.sleep(1)
        #creating a new user in the table
        db.execute(f"""INSERT INTO users 
        (
            username, email, reference_link, my_reference_link,
            balance, reference_bonus, clicks, reference_count, password, created_at
        )
        VALUES(
            '{res['username']}', '{res['email']}','{res['reference_link']}', '{res['my_refere_link']}',
            '10000', '{res['reference_bonus']}', '{res['clicks']}','{res['reference_count']}',
            '{res['password']}','{res['created_at']}'
        )
        """)
        db_conexions.commit()
        time.sleep(1)
        db.execute(f"""INSERT INTO refers_list (id, username, email)
            VALUES('{res['reference_link']}', '{res['username']}', '{res['email']}')
        """)
        db.execute(f"""INSERT INTO ibonx (id, titler, sms, icon, state, color)
        VALUES('{res['reference_link']}','PiggyCoin','Alguém acabou por registrar com o teu código vá página de referências para ver quem foi.','person','','transparent')
        """)
        db.execute(f"INSERT INTO ibonx_count (id) VALUES('{res['reference_link']}')")
        # makig comit
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
        balances = res['balance']
        get_balance = int(balances)
        user = db_moduls.findAll(f"users WHERE my_reference_link='{ids}' ")
        data = user[0]
        if data['my_reference_link'] == data['reference_link']:
            balance = int(data['balance'])
            clicks = int(data['clicks'])
            update_clicks = clicks + 1
            update_balance = balance + get_balance
            db.execute(f"UPDATE users SET balance='{update_balance}', clicks='{update_clicks}' WHERE my_reference_link='{ids}' ")
            db_conexions.commit()
            return {"sms": "sucess for admin"}
        else:
            user2 = db_moduls.findAll(f"users WHERE my_reference_link='{data['reference_link']}' ")
            data2 = user2[0]
            reference_bonus = int(data2['reference_bonus'])
            refere_balance = int(data2['balance'])
            update_refere_bonus = reference_bonus + 10
            update_refere_balance = refere_balance + 10
            balance = int(data['balance'])
            update_balance = balance + get_balance
            clicks = int(data['clicks'])
            update_clicks = clicks + 1

            db.execute(f"UPDATE users SET balance='{update_balance}', clicks='{update_clicks}' WHERE my_reference_link='{ids}' ")
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
        valor = int(res['valor'])
        user = db_moduls.findAll(f"users WHERE my_reference_link='{ids}' ")
        data = user[0]
        balance = int(data['balance'])
        rest_values = balance - valor
        db.execute(f"UPDATE users SET balance='{rest_values}', reference_bonus='0' WHERE my_reference_link='{ids}' ")
        db.execute(f""" 
            INSERT INTO users_payment_forms 
            (id, username, back_name, iban, number, valor, created_at)
            VALUES(
                '{ids}','{res['username']}','{res['back_name']}','{res['iban']}',
                '{res['number']}','{res['currency']}','{res['created_at']}'
            )
        """)
        db.execute(f""" 
            INSERT INTO users_total_pays 
            (id, username, back_name, iban, number, valor, status, created_at)
            VALUES(
                '{ids}','{res['username']}','{res['back_name']}','{res['iban']}',
                '{res['number']}','{res['currency']}','Just payed','{res['created_at']}'
            )
        """)
        db_conexions.commit()
        return {"sms": "sucess"}
    # app_pay2ads_create_users_ibonxs
    @app.post('/app_pay2ads_create_users_ibonxs')
    async def app_pay2ads_create_users_ibonxs(req: Request):
        res = await req.json()
        db.execute(f"""INSERT INTO ibonx (id, titler, sms, icon, state, color)
        VALUES('{res['id']}','{res['titler']}','{res['sms']}','{res['icon']}','{res['state']}','{res['color']}')
        """)
        db.execute(f"INSERT INTO ibonx_count (id) VALUES('{res['id']}')")
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

    # app_pay2ads_update_user_password
    @app.post('/app_pay2ads_update_offers_bonus')
    async def app_pay2ads_update_offers_bonus(req: Request):
        datas = await req.json()
        update_offers(types=datas["types"], datas=datas)
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
    @app.post('/app_pay2ads_admin_delete_payments')
    async def app_pay2ads_get_publish_ads_by_user(req: Request):
        res = await req.json()
        ids = res['id']
        db.execute(f"DELETE FROM users_payment_forms WHERE id='{ids}' ")
        db_conexions.commit()
        return {"sms": "sucess"}
    # app_pay2ads_adim_get_publish_ads_by_user
    @app.post('/app_pay2ads_adim_get_all_users')
    async def app_pay2ads_adim_get_publish_ads_by_user(req: Request):
        data = db_moduls.findAll(f"users")
        return {"data": data}
    # app_pay2ads_adim_get_user_request_form users_total_pays
    @app.post('/app_pay2ads_adim_get_user_request_form')
    async def app_pay2ads_adim_get_user_request_form(req: Request):
        data = db_moduls.findAll(f"users_payment_forms")
        return {"data": data}
    #users_total_pays
    @app.post('/app_pay2ads_adim_get_all_user_payed')
    async def app_pay2ads_adim_get_user_request_form(req: Request):
        data = db_moduls.findAll(f"users_total_pays")
        return {"data": data}
    # 

    # ============================ post methods =============================================
    # router to create new user accounts
    @app.post('/app_pay2ads_get_user_inbox_count_data')
    async def app_pay2ads_get_user_inbox_count_data(req: Request):
        res = await req.json()
        ids = res['id']
        data = db_moduls.findAll(f"ibonx_count WHERE id='{ids}' ")
        print(data)
        print(ids)
        return {"data": data}
    # app_pay2ads_delete_user_inbox_count_data
    @app.post('/app_pay2ads_delete_user_inbox_count_data')
    async def app_pay2ads_delete_user_inbox_count_data(req: Request):
        res = await req.json()
        ids = res['id']
        db.execute(f"DELETE FROM ibonx_count WHERE id='{ids}' ")
        db_conexions.commit()
        return {"data": "sucess"}
    # app_pay2ads_get_user_inbox_data
    @app.post('/app_pay2ads_get_user_inbox_data')
    async def app_pay2ads_get_user_inbox_data(req: Request):
        res = await req.json()
        ids = res['id']
        data = db_moduls.findAll(f"ibonx WHERE id='{ids}' ")
        return {"data": data}
    # app_pay2ads_get_user_refers_data
    @app.post('/app_pay2ads_get_user_refers_data')
    async def app_pay2ads_get_user_refers_data(req: Request):
        res = await req.json()
        ids = res['id']
        data = db_moduls.findAll(f"refers_list WHERE id='{ids}' ")
        return {"data": data}






    












    db_conexions.commit()
except Exception as e:
    print(f"erro ao conectar {e}")







