import time as t
from app import app, db
from app import schemas, models
import pprint as pp
import requests, json
from app import models, schemas
import datetime
import threading

once_flag = True
sec_break = False
break_flag = True
stores = {}

def add_and_get_store():
    global stores
    # len_store = len(models.Store.query.all())
    # if len_store == 0:
    #     store = models.Store(
    #         store_title = "Smamz",
    #         store_description = "Nul",
    #         store_url = "smamz.pk"
    #     )
    #     db.session.add(store)
    #     db.session.commit()
    # else:
    #     stores = schemas.store_schema.dump(models.Store.query.all()[0])
    # stores = schemas.store_schema.dump(models.Store.query.all()[0])
    stores = schemas.stores_schema.dump(models.Store.query.all())
    # print(stores)


def get_varients(lis):
    varient = {}
    for item in lis:
        # varient[str(item['id'])] = {    // store id as a string
        varient[item['id']] = {
            "title":item['title'],
            "price":item['price'],
            "updated":item['updated_at']
        }
    return varient

def print_things(took,dom,obj):
    # flag = once_flag
    global once_flag
    if once_flag:
        for doms in dom:
            if True:
                pp.pprint(doms)
                pp.pprint("--------------------------------")
                try:
                    pp.pprint(obj[doms])
                except:
                    pp.pprint("Error: Domain error")
                pp.pprint("--------------------------------")
                pp.pprint(f"Time took: {int(took)}ms")
        if sec_break:
            # once_flag = False
            print(" \n \n Setting Flag, EOF>>")
    if sec_break:
        once_flag = False

# def add_sales(item_id :int, url: str, ):
#     pass

def add_to_db(lis):
    for thing in lis:
        exis = models.StoreInventory.query.get(thing['id'])
        if exis:
            exis.price = thing['price']
            exis.item_name = thing['title']
            exis.item_url = thing['url']
            exis.item_image_url = thing['image_url']

            if not exis.update_check(thing['updated']):
                # sale = models.Sales.query.filter_by(item_id=exis.id).first()
                dt = datetime.date.today().isoformat().replace('-','')
                s_id = f"{dt}-{exis.id}"
                sale = models.Sales.query.get(s_id)
                if sale:
                    sale.sales_update()
                    # db.session.commit()
                else:
                    sales = models.Sales(
                        id = s_id,
                        item_id = exis.id,
                        sales_store = thing['store_url'],
                        sales = 1
                    )
                    db.session.add(sales)
                    # db.session.commit
            exis.item_updated = thing['updated']
            # items = exis(
            #     id = thing['id'],
            #     item_base_id = thing['base_id'],
            #     item_name = thing['title'],
            #     item_price = thing['price'],
            #     item_url = thing['url'],
            #     item_image_url = thing['image_url'],
            #     in_store = thing['store_id'],
            #     item_updated = thing['updated'],
            # )
        else:
            items = models.StoreInventory(
                id = thing['id'],
                item_base_id = thing['base_id'],
                item_name = thing['title'],
                item_price = thing['price'],
                item_url = thing['url'],
                item_image_url = thing['image_url'],
                in_store = thing['store_id'],
                item_updated = thing['updated'],
            )
            db.session.add(items)
        db.session.commit()       
    print('done??')

def img_url(url):
    if url:
        return url[0]['src']
    else:
        return "https://i.imgur.com/Ne21Znf.jpg"

def data_scrapper():
    # i = 0
    while True:
        # dom_list = [{"store_url":"naja.co"},{"store_url":"hiutdenim.co.uk"}]
        dom_list = stores
        # dom_list = []
        dom_push_list = []
        usable_data = []
        dom_data = {}
        x = datetime.datetime.now()
        # print(f"{dom_list[0]['store_url']}")
        # print(type(x))
        for doms in dom_list:
            data_req = requests.get(f"https://{doms['store_url']}/products.json?limit=0")
            # print(data_req.content.__str__())
        # break
            try:
                data = data_req.json()
                # print(data['products'][0]['title'])
                dom_push_list.append(doms['store_url'])
                for product in data['products']:
                    all_vai = get_varients(product['variants'])
                    vai_keys = all_vai.keys()
                    # print(vai_keys)
                    for vari in vai_keys:
                        # print(all_vai[vari])
                        usable_data.append({
                            "id":vari,
                            "title":f"{product['title']} ({all_vai[vari]['title']})",
                            "price":all_vai[vari]['price'],
                            "url":f"https://{doms['store_url']}/products/{product['handle']}",
                            "image_url": img_url(product['images']),
                            "base_id" : product['id'],
                            "updated":all_vai[vari]['updated'],
                            "store_id":doms['id'],
                            "store_title":doms['store_title'],
                            "store_url":doms['store_url'],
                        })
                dom_data[doms['store_url']] = usable_data
            except Exception as e:
                pp.pprint(f'Error: {e}')
        
        y = datetime.datetime.now()

        

        diff = y-x
        print_things(diff.microseconds/1000,dom_push_list,dom_data)
        if int(diff.microseconds/1_000) <  30_000:
            sl = (30_000-int(diff.microseconds/1_000))*0.001
            t.sleep(sl)
        add_to_db(usable_data)
        dom_push_list = []
        # i = i+1
        # print(i)
        if break_flag:
            break


# t = threading.Thread(target=data_scrapper,daemon=True)
# t.start()
add_and_get_store()
data_scrapper()