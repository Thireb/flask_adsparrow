import json
from urllib.parse import urlparse
from rich import print as rp
from app import app, db
from flask import Flask,render_template, redirect, url_for, current_app, flash, request, jsonify, Response
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from re import fullmatch,compile
import requests as reqs
from app import schemas, models
from typing import Any
from datetime import date as d
import datetime as dt


email_re = compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


login = LoginManager(app=app)
login.login_view = 'register_view_user'

# Render Templates

_both = ["GET", "POST"]
_get = ["GET"]
_post = ["POST"]

@app.route('/',methods=_get)
def root_route():
  if current_user.is_authenticated:
      return redirect(url_for('user_dash'))
  return render_template('index.html')
  # pass


# Pass Operations

@app.route('/dashboard/product/<item_id>',methods=_both)
@login_required
def indv_product(item_id):
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  # print(_name)
  
  return render_template('dashboard/product.html',name=_name,sub=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/domain/products/<id>',methods=_both)
@login_required
def d_all_product(id):
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  
  # print(_name)
  return render_template('dashboard/products.html',name=_name,sub=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/niche/domain/<id>',methods=_get)
@login_required
def n_dom_all(id):
  test_domains = schemas.ustore_schema.dump(models.UStore.query.filter_by(niche_id=id).all())
  _domains = []
  for item in test_domains:
    dom_o = models.Store.query.filter_by(store_url=item['niche_domain']).first()
    prod_c = len(schemas.storeinventory_all_schema.dump(dom_o.inventory))
    dom_dump = schemas.store_schema.dump(dom_o)
    _domains.append({
      "did":dom_dump['id'],
      "name":dom_dump['store_title'],
      "url":dom_dump['store_description'],
      "products_count":prod_c,
      "hidden":item['hidden'],
      "created":dom_dump['date_added'].split('T')[0]
    })
  len_domains = len(_domains)
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  return render_template('dashboard/domains-all.html',name=_name,sub=_sub,domains=_domains,len_domains=len_domains,sub_raw=_sub_raw)





# Products


@app.route('/dashboard/products',methods=_both)
@login_required
def all_product():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  data = []
  niches = current_user.niches
  for niche in niches:
    n_dom = [item for item in niche.niche_stores.all()]
    for items in n_dom:
        dom_a = models.Store.query.filter_by(store_url=items.niche_domain).first()
      # for item in dom_a:
        d_inv = [inv for inv in dom_a.inventory]
        for inv in d_inv:
          fav = False
          if models.Favorites.query.filter_by(id=f"{current_user.id}-{inv.id}").first():
            fav = True
            print(fav)
          data.append({
            "id":inv.id,
            "name":inv.item_name,
            "n_id":niche.id,
            "item_id":inv.id,
            "updated":inv.item_updated.split('T')[0],
            "domain_name":dom_a.store_title,
            "domain":f"https://{dom_a.store_url}",
            "fav":fav,
            "price":inv.item_price,
            "niche":niche.niche_name,
            "pic":inv.item_image_url
          })
  d_len = len(data)
  _sub_raw = sub_check(current_user.subscription)
  return render_template('dashboard/products.html',name=_name,sub=_sub,data=data,d_len=d_len,sub_raw=_sub_raw)

@app.route('/dashboard/saveproducts',methods=_both)
@login_required
def save_all_product():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  data = []
  niches = current_user.niches
  for niche in niches:
    n_dom = [item for item in niche.niche_stores.all()]
    for items in n_dom:
        dom_a = models.Store.query.filter_by(store_url=items.niche_domain).first()
      # for item in dom_a:
        d_inv = [inv for inv in dom_a.inventory]
        for inv in d_inv:
          if models.Favorites.query.filter_by(id=f"{current_user.id}-{inv.id}").first():
            data.append({
            # "id":inv.id,
            "name":inv.item_name,
            "n_id":niche.id,
            "item_id":inv.id,
            "updated":inv.item_updated.split('T')[0],
            "domain_name":dom_a.store_title,
            "domain":f"https://{dom_a.store_url}",
            "fav":True,
            "price":inv.item_price,
            "niche":niche.niche_name,
            "pic":inv.item_image_url
          })
  d_len = len(data)
  _sub_raw = sub_check(current_user.subscription)
  return render_template('dashboard/save-products.html',name=_name,sub=_sub,data=data,d_len=d_len,sub_raw=_sub_raw)


# Auth

@app.route('/login',methods=_both)
def login_view_user():
  error = None
  if current_user.is_authenticated:
        return redirect(url_for('user_dash'))
  if request.method == "POST":
        _username = request.form.get("email-username")
        _remember = False

        if(request.form.get("remember")=='on'):
          _remember = True
        if(email_validation(_username)):
          user = models.User.query.filter_by(email=_username).first()
        else:
          user = models.User.query.filter_by(username=_username).first()
        # print(user.check_password(request.form.get("password")))
        if user is None or not user.check_password(request.form.get("password")):
            # flash('Invalid Username or Password')
            # return redirect(url_for('login_view_user'))
            error = "Wrong username/password"
            return render_template('login.html',error=error)
        login_user(user, force=True,remember=_remember)
        # flash("Login Successful")
        # next_page = request.args.get('next')
        # if not next_page or url_parse(next_page).netloc != '':
            # next_page = url_for('admin_home')
        return redirect(url_for('user_dash'))
  return render_template('login.html',error=error)
  # pass

@app.route('/register',methods=_both)
def register_view_user():
    if current_user.is_authenticated:
        return redirect(url_for('user_dash'))
    if request.method == "POST":
      _username=request.form.get("username")
      f = request.form.get("firstName")
      l = request.form.get("lastName")
      _state=request.form.get("state")
      _address=request.form.get("address")
      _zip=request.form.get("zipCode")
      _country=request.form.get("country")
      _name = f"{f}|{l}"
      _email=request.form.get("email")
      _password=request.form.get("password")
      _terms=request.form.get("terms")
      print(_terms)
      print(type(_terms))
      if(_terms=='off'):
        return redirect(url_for('register_view_user'))
      user = models.User.query.filter_by(username=_username).first()
      if user and not user.is_deleted:
        return redirect(url_for('register_view_user'))
      new_user = models.User(
          country=_country,
          state=_state,
          zipcode=int(_zip),
          address=_address,
          username=_username,
          password=_password,
          name=_name,
          email=_email,
          date_of_birth="01-01-2001",
          is_deleted=False,
      )
      new_user.set_token()
      add(new_user)
      login_user(new_user, force=True)
      next_page = request.args.get('next')
      if not next_page or urlparse(next_page).netloc != '':
        next_page = url_for('user_dash')
      return redirect(next_page)
    return render_template('register.html')
  # if current_user.is_authenticated:
  #       return redirect(url_for('user_dash'))
  # pass

@app.route('/logout',methods=_get)
@login_required
def view_logout():
  logout_user()
  return redirect(url_for('root_route'))

# Settings ???
@app.route('/dashboard/accountsettings',methods=_both)
@login_required
def user_set():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  # print(_name)
  return render_template('dashboard/account-settings.html',name=_name,sub=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/viewbilling',methods=_both)
@login_required
def user_pay():
  _sub_raw = sub_check(current_user.subscription)
  _name = current_user.username
  fname = current_user.name.split("|")
  _sub = sub_check(current_user.subscription)
  _until = current_user.subscription_until
  _delta = (str_to_date(str(_until))-d.today()).days
  usercards = current_user.user_card.all()
  days=0
  if _sub['tier'] <= 3 and _sub['tier'] !=0 :
    days=30
    _delta_diff_raw = _delta - days
    _delta_diff = int((_delta_diff_raw/30)*100)
  elif _sub['tier'] > 3 and _sub['tier'] <=6 and _sub['tier'] !=0:
    days=360
    _delta_diff_raw = _delta - days
    _delta_diff = int((_delta_diff_raw/360)*100)
  else:
    days=7
    _delta_diff_raw = _delta - days
    _delta_diff = int((_delta_diff_raw/7)*100)
      
  if request.method == "POST":
    if "upgradePlan-Form" in request.form:
      x = request.form.get("choosePlan")
      return redirect(url_for("user_upgrade",set=x))
  # print(_name)
  return render_template('dashboard/view-billing.html',name=_name,sub=_sub['tier_name'], until=_until, delta=_delta, diff=_delta_diff,days=days,fname=fname,usercards=usercards,subsc=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/pricing',methods=_both)
@login_required
def user_price():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  # print(_name)
  return render_template('dashboard/pricing.html',name=_name,sub=_sub,sub_raw=_sub_raw)

#Settings Functions

@app.route('/dashboard/user/tier',methods=_both)
@login_required
def user_upgrade():
  arg = request.args.get('set')
  if arg == "Choose Plan":
    return redirect(url_for("user_pay"))
  elif int(arg) == 0:
    return redirect(url_for("user_pay"))
  current_user.subscription = int(arg)
  # current_user.subscription_days_left = str(d.today() +  dt.timedelta(days=30))
  if int(arg) <= 3:
    current_user.subscription_until = str(d.today() +  dt.timedelta(days=30))
  elif int(arg) > 3 and int(arg) <= 6:
    current_user.subscription_until = str(d.today() +  dt.timedelta(days=360))
  current_user.subscription_recuring = True
  # thing = str(d.today()).replace("-","")
  # str_to_date(thing)
  db.session.commit()  
  return redirect(url_for("user_pay"))

# Main Dashboard

@app.route('/dashboard',methods=_get)
@login_required
def user_dash():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  u_s = current_user.user_store
  s_s = []
  p_s = []
  f_s = []
  inv_count = 0
  for items in u_s:
    s = models.Store.query.filter_by(store_url=items.niche_domain).first()
    if s not in s_s:
      s_s.append(s)
  for itemd in s_s:
    inv = itemd.inventory
    inv_count = inv_count + len(itemd.inventory.all())
    for itemi in inv:
      sal = itemi.item_sales
      for itemss in sal:
        if itemss and itemss.id.split('-')[0] == d.today().isoformat().replace('-',''):
          p_s.append(itemss)
  all_sales = models.Sales.query.order_by(models.Sales.sales).all()
  for itemx in all_sales:
    for itemy in p_s:
      if itemy == itemx:
        f_s.append(itemx)
  tmp = [i for i in f_s]
  top = []
  top_f = []
  top_f_f = False
  for x in tmp:
    xy = models.StoreInventory.query.get(x.item_id)
    top.append({
        "name":xy.item_name,
        "img":xy.item_image_url,
        "domain":x.sales_store,
        "sale":x.sales,
        "price":xy.item_price,
        "rev":x.sales*xy.item_price
      })
  if len(top) > 5:
    top_f=top
  else:
    top_f=top[:5]
  
  if len(top_f) != 0:
    top_f_f = True
  
  return render_template('dashboard/index.html',name=_name,sub=_sub,sub_raw=_sub_raw,top=top_f,check_f=top_f_f,inv_count=inv_count)

# Domains

@app.route('/dashboard/activedomain',methods=_get)
@login_required
def user_dom_active():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  # print(_name)
  return render_template('dashboard/domains.html',name=_name,sub=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/expdomain',methods=_get)
@login_required
def user_dom_exp():
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  # print(_name)
  return render_template('dashboard/domain-ex.html',name=_name,sub=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/alldomain',methods=_get)
@login_required
def user_dom_all():
  test_domains = schemas.ustore_schema.dump(current_user.user_store)
  _domains = []
  for item in test_domains:
    dom_o = models.Store.query.filter_by(store_url=item['niche_domain']).first()
    prod_c = len(schemas.storeinventory_all_schema.dump(dom_o.inventory))
    dom_dump = schemas.store_schema.dump(dom_o)
    _domains.append({
      "did":dom_dump['id'],
      "name":dom_dump['store_title'],
      "url":dom_dump['store_description'],
      "products_count":prod_c,
      "hidden":item['hidden'],
      "created":dom_dump['date_added'].split('T')[0]
    })

  len_domains = len(_domains) != 0
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  return render_template('dashboard/domains-all.html',name=_name,sub=_sub,domains=_domains,len_domains=len_domains,sub_raw=_sub_raw)

@app.route('/dashboard/adddomain',methods=_both)
@login_required
def add_domain():
  # pre reqs
  niches = []
  _niches = schemas.niches_schema.dump(current_user.niches)
  for nich in _niches:
    niches.append([nich['id'],nich['niche_name']])
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  error = []
  #if
  if request.method == "POST":
    _get_dom = request.form.get('domain')
    _nid = request.form.get('nid')
    domain = _get_dom.replace("https://","").rstrip('/')
    domain = domain.replace("www.","")
    check = False
    try:
      dom_test = reqs.get(f"https://{domain}/products.json?limit=0")
      check = dom_test.status_code != 200
      if check:
        error.append('Error: wrong domain or not a shopify domain')
    except Exception as e:
      check = True
      error.append(f'Error: {e}')
    if check:
      return render_template('dashboard/adddomain.html',name=_name,sub=_sub, niches=niches, error=error,sub_raw=_sub_raw)
    # all_doms = schemas.stores_schema.dump(models.Store.query.all())
    if not models.Store.query.filter_by(store_url=domain).first():
      m_s = models.Store(
        store_title = domain.split('.')[0],
        store_url = domain,
        store_description = f"https://{domain}/"
      )
      add(m_s)
    exists_flag = False
    n_stors = models.UStore.query.filter_by(niche_id=_nid).all()
    for ns in n_stors:
      exists_flag = ns.niche_domain == domain
    
    if exists_flag:
      error.append('Error: domain already exists in niche')
      return render_template('dashboard/adddomain.html',name=_name,sub=_sub, niches=niches, error=error,sub_raw=_sub_raw)

    n_us = models.UStore(
      niche_domain=domain,
      niche_id = _nid,
      of_user = current_user.id
    )
    add(n_us)
    return redirect(url_for('niche_dash'))
  return render_template('dashboard/adddomain.html',name=_name,sub=_sub, niches=niches, error=error,sub_raw=_sub_raw)

@app.route('/dashboard/hiddendomain',methods=_get)
@login_required
def user_dom_hid():
  test_domains = schemas.ustore_schema.dump(current_user.user_store)
  _domains = []
  for item in test_domains:
    dom_o = models.Store.query.filter_by(store_url=item['niche_domain']).first()
    prod_c = len(schemas.storeinventory_all_schema.dump(dom_o.inventory))
    dom_dump = schemas.store_schema.dump(dom_o)
    if item['hidden']:
      _domains.append({
        "did":dom_dump['id'],
        "name":dom_dump['store_title'],
        "url":dom_dump['store_description'],
        "products_count":prod_c,
        "hidden":item['hidden'],
        "created":dom_dump['date_added'].split('T')[0]
      })
  len_domains = len(_domains) != 0
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  # print(_name)
  return render_template('dashboard/domains-hidden.html',name=_name,sub=_sub,domains=_domains,len_domains=len_domains,sub_raw=_sub_raw)

@app.route('/dashboard/hidedomain/<did>',methods=_get)
@login_required
def user_dom_hid_active(did : int):
  dom = models.UStore.query.get(did)
  dom.set_hidden()
  db.session.commit()
  return redirect(url_for('user_dom_hid'))

@app.route('/dashboard/showdomain/<did>',methods=_get)
@login_required
def user_dom_hid_vis(did : int):
  dom = models.UStore.query.get(did)
  dom.set_visible()
  db.session.commit()
  return redirect(url_for('user_dom_all'))

# Niches
@app.route('/dashboard/niche',methods=_both)
@login_required
def niche_dash():
  _niches_obj = current_user.niches
  _niches_dump = schemas.niches_schema.dump(_niches_obj)
  _u_doms = current_user.user_store
  _u_doms_dump = schemas.ustore_schema.dump(_u_doms)
  _niches = []
  _today = d.today().isoformat().replace('-','')
  for nich in _niches_dump:
    # niche domains
    n_d = []
    n_h_d = []
    # products of all domains
    t_p = 0
    t_sale = 0
    for dom in _u_doms_dump:
      if dom['niche_id'] == nich['id']:
        n_d.append(dom['niche_domain'])
        if dom['hidden']:
          n_h_d.append(dom["hidden"])
        for dms in n_d:
          stor = models.Store.query.filter_by(store_url=dms).first()
          stor_inv_dump = schemas.storeinventory_all_schema.dump(stor.inventory)
          for items in stor_inv_dump:
            sl = models.Sales.query.get(f"{_today}-{items['id']}")
            if sl:
              t_sale=t_sale+schemas.sale_schema.dump(sl)['sales']
          t_p = t_p + len(stor_inv_dump)
    n_d_l = len(n_d)
    n_h_d_l = len(n_h_d)
    # t_p_l = len(t_p)
    _niches.append(
      {
        'id':nich['id'],
        'niche_name':nich['niche_name'],
        'niche_domains':n_d_l,
        'hidden_domains':n_h_d_l,
        'total_products':t_p,
        'total_sales' : t_sale
      }
    )

  _len = len(_niches)
  _flag = len(_niches)!=0
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  return render_template('dashboard/niche.html',name=_name, len=_len,sub=_sub,niches=_niches,flag=_flag,sub_raw=_sub_raw)

@app.route('/dashboard/addniche',methods=_both)
@login_required
def add_niche():
  if request.method == "POST":
    user = current_user
    # l = []
    add_niche = request.form.get("add-niche")
    niche = models.Niche(
      niche_name = add_niche,
      niche_user_ = user.id
    )
    # user.set_niche_user(json.dumps(niche))
    db.session.add(niche)
    db.session.commit()
    return redirect(url_for('niche_dash'))
  _name = current_user.username
  _sub = sub_check(current_user.subscription)['tier_name']
  _sub_raw = sub_check(current_user.subscription)
  return render_template('dashboard/addniche.html',name=_name,sub=_sub,sub_raw=_sub_raw)

@app.route('/dashboard/delniche/<nid>',methods=_get)
@login_required
def del_niche(nid : int):
  niche = models.Niche.query.filter_by(id=nid).first()
  for ustores in niche.niche_stores.all():
    delete(ustores)
  delete(niche)
  return redirect(url_for('niche_dash'))

# Non Login Methods
@app.route('/about')
def st_about():
  if current_user.is_authenticated:
      return redirect(url_for('user_dash'))
  return render_template("about.html")

@app.route('/contact')
def st_contact():
  if current_user.is_authenticated:
      return redirect(url_for('user_dash'))
  return render_template("contact.html")

@app.route('/pricing')
def st_pricing():
  if current_user.is_authenticated:
      return redirect(url_for('user_dash'))
  return render_template("pricing.html")

@app.route('/privacypolicy')
def st_privacy():
  if current_user.is_authenticated:
      return redirect(url_for('user_dash'))
  return render_template("privacy-policy.html")


@app.route('/termsandconditions')
def st_terms():
  if current_user.is_authenticated:
      return redirect(url_for('user_dash'))
  return render_template("terms-and-conditions.html")

# # Favorite routes
# @app.route('/products/favorites')
# def view_user_favorites():
#   if current_user.is_authenticated:
#     fav_list = view_favorites(current_user.id)
#     if len(fav_list) == 0:
#       return Response("no Favorites"), 200
#     else:
#       return Response(fav_list), 200

@app.route('/add_fav/<item_id>')
@login_required
def add_user_favorites(item_id):
  # if item_id not in view_favorites(current_user.id):
  add_favorites(current_user.id, item_id)
  return redirect(url_for("all_product"))

@app.route('/del_fav/<item_id>')
@login_required
def delete_user_favorites(item_id):
  # if item_id in view_favorites(current_user.id):
    # delete_favorite(current_user.id, item_id)
  delete_favorite(current_user.id, item_id)
  return redirect(url_for("all_product"))
  
    

# Other Methods
def add(object):
  db.session.add(object)
  db.session.commit()

def delete(object):
  db.session.delete(object)
  db.session.commit()

# strip time with impunity
def str_to_date(obj):
  try:
    obj = obj.replace('-','')
  except:
    pass
  date_string = f"{obj[0]}{obj[1]}{obj[2]}{obj[3]}-{obj[4]}{obj[5]}-{obj[6]}{obj[7]}"
  return dt.datetime.strptime(date_string,'%Y-%m-%d').date()

# Login Loader
@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))

# Sub Check
def sub_check(obj):
  check = obj
  ret = {}
  _until = current_user.subscription_until
  _delta = (str_to_date(str(_until))-d.today()).days
  if check <= 3 and check !=0 :
    days=30
    _delta_diff_raw = _delta - days
    _delta_diff = int((_delta_diff_raw/30)*100)
  elif check > 3 and check <=6 and check !=0:
    days=360
    _delta_diff_raw = _delta - days
    _delta_diff = int((_delta_diff_raw/360)*100)
  else:
    days=7
    _delta_diff_raw = _delta - days
    _delta_diff = int((_delta_diff_raw/7)*100)
  if check == 0:
    store_track = 1
    niche_track = 1
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Trial","tier":check,"price":"FREE [Trial]","time": "7days"}
  elif check == 1:
    store_track = 5
    niche_track = 5
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Starter","tier":check,"price":"34", "time": "month"}
  elif check == 2:
    store_track = 50
    niche_track = 10
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Professional","tier":check,"price":"99", "time": "month"}
  elif check == 3:
    store_track = 250
    niche_track = 50
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Entreprise","tier":check,"price":"300", "time": "month"}
  elif check == 4:
    store_track = 10
    niche_track = 5
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Basic","tier":check,"price":"228", "time": "year"}
  elif check == 5:
    store_track = 25
    niche_track = 7
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Standard","tier":check,"price":"348", "time": "year"}
  elif check == 6:
    store_track = 50
    niche_track = 10
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"Premium","tier":check,"price":"588", "time": "year"}
  else:
    store_track = 999
    niche_track = 999
    retr = lim_avail(niche_t=niche_track,store_t=store_track,)
    ret={"tier_name":"[ERROR]","tier":99,"price":"INF", "time": "IND"}
  ret["delta"]=_delta_diff_raw
  ret["delta_perc"]=_delta_diff
  ret["p_days"]=days
  ret["limit"]=retr
  return ret

# Limitation

def lim_avail(niche_t,store_t):
  tmp = {}
  tmp['niche_done'] = False
  tmp['store_done'] = False
  usr = current_user
  # print(usr.niches)
  n_c = len(usr.niches.all())
  u_c = len(usr.user_store.all())
  tmp['niche_curr'] = n_c
  tmp['store_curr'] = u_c
  tmp['niche_avail'] = niche_t
  tmp['store_avail'] = store_t
  if n_c - niche_t == 0:
    tmp['niche_done'] = True
  if u_c - store_t == 0:
    tmp['store_done'] = True
  return tmp

# Email Validation
def email_validation(email):
  if fullmatch(email_re, email):
    return True
  else:
    return False

# Favorites thingy
def add_favorites(userid, itemid):
  fav_to_add = f"{userid}-{itemid}"
  fav = models.Favorites(id=fav_to_add)
  add(fav)
  
def view_favorites(userid):
  items = models.Favorites.query.all()
  user_fav = [item.id for item in items if item.id.__contains__(f'{userid}')]
  return user_fav

def delete_all_favorite(userid):
  items = models.Favorites.query.all()
  user_fav = [item.id for item in items if item.id.__contains__(f'{userid}')]
  for item in user_fav:
    to_del = models.Favorites.query.get(item)
    delete(to_del)
    
def delete_favorite(userid, itemid):
  delete(models.Favorites.query.filter_by(id=f"{userid}-{itemid}").first())
# End Favorites thingy