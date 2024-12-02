from . import ma

class User_Schema(ma.Schema):
    class Meta:
        fields = (
            'id', 
            'username', 
            'email', 
            'name', 
            "date_of_birth", 
            "is_deleted", 
            "about_user", 
            "sign_up_time",
            "subscription",
            "subscription_days_left",
            "is_activated",
            "store_limit"
        )

class Store_Schema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "store_title",
            "store_description",
            "store_url",
            "date_added",
            "subbed_user",
            "is_active",
            "is_deleted",
        )

class Niche_Schema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "niche_name",
        )

class StoreInventory_Schema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "item_name",
            "item_price",
            "item_base_id",
            "item_varient_id",
            "item_url",
            "time_added",
            "time_edited",
            "is_deleted",
        )

class Ustore_Schema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "niche_domain",
            "niche_id",
            "hidden",
        )

class Sales_Schema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "sales",
        )
        
store_schema = Store_Schema()
stores_schema = Store_Schema(many=True)
user_schema = User_Schema()
users_schema = User_Schema(many=True)
niche_schema = Niche_Schema()
niches_schema = Niche_Schema(many=True)
storeinventory_schema = StoreInventory_Schema()
storeinventory_all_schema = StoreInventory_Schema(many=True)

# Single Item
sale_schema = Sales_Schema()

# Many things
sales_schema = Sales_Schema(many=True)
ustore_schema = Ustore_Schema(many=True)
