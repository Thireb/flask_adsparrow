from email.policy import default
from app import app, db, ma, schemas
from datetime import datetime as dt
from datetime import date as d
import datetime as dtl
import random

# Tables
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False)
    email = db.Column(db.String, index=True, nullable=False)
    password = db.Column(db.String, index=False, nullable=False)
    name = db.Column(db.String, index=True, nullable=False)
    date_of_birth = db.Column(db.String)
    about_user = db.Column(db.String, default=f"Hi I am User {username}")
    sign_up_time = db.Column(db.String, default= f"{dt.now().isoformat()}")
    token = db.Column(db.String, unique=True)
    
    # Some New Entries
    country = db.Column(db.String,)
    state = db.Column(db.String)
    zipcode = db.Column(db.Integer)
    address = db.Column(db.String)

    subscription = db.Column(db.Integer, default=0)
    subscription_until = db.Column(db.String,default=str(d.today() +  dtl.timedelta(days=7)))
    subscription_recuring = db.Column(db.Boolean, default=False)

    store_limit = db.Column(db.Integer)

    user_card = db.relationship("Card", backref="_use_card", lazy="dynamic")

    user_store = db.relationship("UStore", backref="_user_doms", lazy="dynamic")
    
    niches = db.relationship("Niche", backref="niche_user", lazy="dynamic")
    
    is_activated = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return True
    
    def change_recurrence(self):
        self.subscription_recuring = not self.subscription_recuring

    def get_id(self):
        return self.id

    def check_password(self, password: str):
        return self.password == password

    def set_about_user(self, about: str):
        self.about_user = about

    def get_token(self):
        return self.token
    
    def delete_user(self):
        self.is_deleted = True
        self.username = f"{self.username}_[DELETED]"
        self.email = f"{self.email}_[DELETED]"
        self.about_user = f"[DELETED]"

    def activate_user(self):
        self.is_activated = True    

    def add_subscription(self, sub_type: str, days_to_add: int,store_limit: int):
        self.subscription = sub_type
        self.subscription_days_left = self.subscription_days_left + days_to_add
        self.store_limit = store_limit
        # pass

    def check_subscription(self):
        subbed_stores = schemas.stores_schema.dump(self.subbed_stores)
        if self.subscription is None:
            return {
                "status": "error",
                "message": "no subscription found", 
                "code": "ea"
            }, False
        elif self.subscription_days_left == 0:
            return {
                "status": "error",
                "message": "Subscription Expired", 
                "code": "ef"
            }, False
        # elif len(subbed_stores) >= self.store_limit:
        #     return {
        #         "status": "error",
        #         "message": "Store Limit Reached", 
        #         "code": "eb"
        #     }
        else:
            return {
                "status": "success",
                "message": "Subscription exists", 
                "days_left": self.subscription_days_left, 
                "subscription_type": self.subscription,
                "store_limit": self.store_limit,
                "stores_subbed": len(subbed_stores),
                'code': "00"
            }, True
    
    def check_for_limit(self):
        subbed_stores = schemas.stores_schema.dump(self.subbed_stores)
        if len(subbed_stores) < self.store_limit:
            return {
                "message": "Store Can Be Added",
                "code": "0a",
                "status": "success"
            }, True
        else:
            return {
                "message": "Store Cannot Be Added",
                "code": "fa",
                "status": "error"
            }, False

    def change_password(self, password: str):
        self.password = password

    def change_name(self, name: str):
        self.name = name
    
    def change_email(self, email: str):
        self.email = email
        
    def set_token(self):
        random_string = ''
        while True:
            for _ in range(16):
                random_integer = random.randint(97, 97 + 26 - 1)
                flip_bit = random.randint(0, 1)
                random_integer = random_integer - 32 if flip_bit == 1 else random_integer
                random_string += (chr(random_integer))
            user = User.query.filter_by(token=random_string).first()
            if not user:
                break
        self.token = random_string

    def __repr__(self) -> str:
        return f"User {self.username}"

class Card(db.Model):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)
    card_name = db.Column(db.String)
    card_number = db.Column(db.Integer)
    card_exp = db.Column(db.String)
    card_ccv = db.Column(db.Integer)
    card_user = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self) -> str:
        return f"Card {self.card_name}"

class Niche(db.Model):
    __tablename__ = "niche"
    id = db.Column(db.Integer,primary_key=True)
    niche_name = db.Column(db.String)
    # niche_link = db.Column(db.String)
    niche_stores = db.relationship("UStore", backref="_niche_id", lazy="dynamic")
    niche_user_ = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def __repr__(self) -> str:
        return f"Niche {self.niche_name}"

class UStore(db.Model):
    __tablename__ = "userstore"
    id = db.Column(db.Integer, primary_key=True)
    niche_domain = db.Column(db.String)
    hidden = db.Column(db.Boolean, default=False)
    niche_id = db.Column(db.Integer, db.ForeignKey("niche.id"))
    of_user = db.Column(db.Integer, db.ForeignKey("users.id"))
    # pass

    def set_hidden(self):
        self.hidden = True
    
    def set_visible(self):
        self.hidden = False

    def __repr__(self) -> str:
        return f"Niche_ID {self.niche_id} || ID {self.id}"

class Store(db.Model):
    '''
    dt.now().isoformat()
    '''
    __tablename__ = "store"
    id = db.Column(db.Integer, primary_key=True)
    store_title = db.Column(db.String, index=True, nullable=False)
    store_description = db.Column(db.String, index=True)
    store_url = db.Column(db.String, index=True)

    date_added = db.Column(db.String, default=f"{dt.now().isoformat()}")

    inventory = db.relationship("StoreInventory", backref="item_store", lazy="dynamic")

    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    def delete_store(self):
        self.is_deleted = True
        self.is_active = False
        for item in self.inventory:
            db.session.delete(item)
            db.session.commit()
            
    def deactivate_store(self):
        self.delete_store()
    
    def __repr__(self) -> str:
        return f"Store_title {self.store_title} || Store_id {self.id}"

class Sales(db.Model):
    __tablename__="sales"
    id = db.Column(db.String, primary_key=True)
    # id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("storeinventory.id"))
    sales_store = db.Column(db.String)
    # sales_date = db.Column(db.String, default=f"{d.today().isoformat().replace('-','')}")
    sales = db.Column(db.Integer)

    def sales_update(self):
        self.sales = self.sales + 1 

    def __repr__(self) -> str:
        return f"Date {self.id} || Sale {self.sales}"

class StoreInventory(db.Model):
    __tablename__="storeinventory"
    id = db.Column(db.Integer, primary_key=True)
    item_base_id = db.Column(db.Integer, nullable=False) 
    # item_varient_id = db.Column(db.Integer, nullable=False) 
    item_name = db.Column(db.String, nullable=False, index=True)
    # item_description = db.Column(db.String, index=True)
    item_price = db.Column(db.String)
    item_updated = db.Column(db.String)
    # item_varient = db.Column(db.String)
    item_sales = db.relationship("Sales", backref="_item_id", lazy="dynamic")
    item_url = db.Column(db.String)
    item_image_url = db.Column(db.String)

    
    time_added = db.Column(db.String, default=f"{dt.now().isoformat()}")
    # time_edited = db.Column(db.String, default=f"{dt.now().isoformat()}")
    
    in_store = db.Column(db.Integer, db.ForeignKey("store.id"))
    
    is_deleted = db.Column(db.Boolean, default=False)
    
    def update_check(self, get_new_date):
        return self.item_updated == get_new_date
    
    def __repr__(self) -> str:
        return f"Item {self.item_name} || in {self.in_store}"

class Favorites(db.Model):
    __tablename__="favorites"
    id = db.Column(db.String, primary_key=True)
            
    def __repr__(self) -> str:
        return f"Item {self.id.split('-')}"
