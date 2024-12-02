#!/usr/bin/env python
# Imports
import json

# SERVER
def run_server(host: str, port: int) -> None:
    from app import app
    if host == None:
        host = '0.0.0.0'
    if port == None:
        port = 5000
    app.run(
        host=host, 
        port=port, 
        debug=True, 
        # ssl_context="adhoc"
    )

# DB
def deploy_app() -> None:
    from app import app, db
    from flask_migrate import upgrade, migrate, init, stamp
    
    app.app_context().push()
    
    db.create_all()
    try:
        init()
    except:
        pass
    stamp()
    migrate()
    upgrade()

def clear_db() -> None:
    from app import app, db, models, admin
    len_admins = len(admin.Admins.query.all())
    if len_admins != 0:
        admin_ = admin.Admins.query.get(1)
        admin_creds = {
            'username': admin_.admin_username,
            'password': admin_.admin_password,
            'token': admin_.admin_token,
        }
    db.session.close()
    db.drop_all()
    db.create_all()
    if len_admins != 0:
        new_admin = admin.Admins(
            admin_username = admin_creds["username"],
            admin_password = admin_creds["password"],
            admin_token = admin_creds["token"],
        )
        db.session.add(new_admin)
        db.session.commit()
    user = models.User(
        username = "dummy_user",
        email = "dummy_email@nowhere.com",
        password = "dummy_password",
        name = "Dummy Name",
        date_of_birth = "09-12-1999",
    )
    user.set_token()
    user_token = user.get_token()
    print("===================\nCleaned DB\n")
    db.session.add(user)
    db.session.commit()
    print("===================\nAdded dummy user\n")
    print(f"User token for testing is {user_token}, \nUser_id is {user.id} \nUsername is {user.username} \nPassword is {user.password}")

# ADMIN
def add_admin() -> None:
    from app import db, app, admin
    deploy_app()
    users = admin.Admins.query.all()
    if len(users) != 0:
        print("\nAdmin was already Added, Are You Sure, you are Not Forgetting the Credentials?")
    else:
        print("Adding an Admin Now, You will be Prompted to enter Username and Password")
        username = input("Username: \n >")
        while True:
            password = input("Password: \n >")
            retype_password = input("Retype Password: \n >")
            if password == retype_password:
                break
        new_admin = admin.Admins(
            admin_username=username,
            admin_password=password,
        )
        new_admin.set_token()
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin Added, Token is {new_admin.get_token()}")

def change_password() -> None:
    from app import db, admin
    if len(admin.Admins.query.all()) != 0:
        admin_ = admin.Admins.query.get(1)
        print("Changing Password For the Existing Admin")
        while True:
            old_password = input("Old Password: \n >")
            if admin_.admin_password == old_password:
                print("Old Password Correct! Continue")
                break
            else:
                print("Old Password Incorrect! Re Enter")
        while True:
            new_password = input("New Password: \n >")
            new_password_re = input("Retype New Password: \n >")
            if new_password == new_password_re:
                print(f"Password Updated for user {admin_.admin_username}")
                break
        admin_.change_password(new_password)
        db.session.commit()
    else:
        print("No Admin Added, add with -addadmin")

def get_admin_token() -> None:
    from app.admin import Admins
    if len(Admins.query.all()) != 0:
        i = 0
        while i < 3:
            admin = Admins.query.get(1)
            print(f"For {admin.admin_username}")
            password = input("Type Password: \n >")
            if admin.admin_password == password:
                token = admin.get_token()
                print(token)
                break
            else:
                print("Password Wrong, Again")
            i += 1
        if i == 3:
            print("you are Out Of Tries, if this wasn't you, change your password immediately")
    else:
        print("No Admin Added, Add With -addadmin")

# Tests
def get_test_creds() -> None:
    from app.models import User
    from app.schemas import user_schema
    user = User.query.get(1)
    result = user_schema.dump(user)
    result["token"] = user.get_token()
    result['password'] = user.password
    print(json.dumps(result, indent=4, sort_keys=False))

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Run this server", epilog="Have Fun")
    server_group = parser.add_argument_group("Flask Application")
    server_group.add_argument("-runserver", default=False, action="store_true", help='Run Flask Application with default host and port, Can Change in -host and -port')
    server_group.add_argument("-host", type=str, default="0.0.0.0", help='Change the host ip of Flask Server, To Access it on other PC\'s, Use 0.0.0.0')
    server_group.add_argument("-port", type=int, default=5000, help="Enter the Port Manually")
    # DB Group
    db_group = parser.add_argument_group('Database Functions')
    db_group.add_argument("-deploy", default=False, action="store_true", help="It initializes the db models in the models.py file.... stamps it, migrates it, and upgrades it")
    db_group.add_argument('-cleardb', default=False, action="store_true", help="Clears the DB")
    # Admin Group
    admin_group = parser.add_argument_group("Admin Functions")
    admin_group.add_argument("-addadmin", action="store_true", help="Adds An Admin")
    admin_group.add_argument("-changepassword", action="store_true", help="Changes Admin Password")
    admin_group.add_argument('-getadmintoken', action="store_true", help="Gets Admin Token")
    # Testing Purposes
    test_group = parser.add_argument_group("Testing")
    test_group.add_argument("-getdummy", action="store_true", help="Gets Test Dummy Information for Testing Purpose Only")
    
    args = parser.parse_args()
    # Server
    if args.runserver:
        run_server(host=args.host, port=args.port)
    # DB
    if args.deploy:
        deploy_app()
    if args.cleardb:
        clear_db()
    # Admin
    if args.addadmin:
        add_admin()
    if args.changepassword:
        change_password()
    if args.getadmintoken:
        get_admin_token()
    # Test
    if args.getdummy:
        get_test_creds()
    
