from re import fullmatch,compile
from flask import Flask, request, jsonify, Response
# from flask.wrappers import Response
from app import app, db
from app import schemas, models
from typing import Any

email_re = compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

get_only = ["GET"]
post_only = ["POST"]
both_ = ["GET", "POST"]

@app.route('/api/server_status')
def base() -> Response:
    return Response("Server Running.....")

# USERS
@app.route('/api/login')
def login() -> str:
    """Checks Login Information with the db
    Format
    data = {
        "username": str -> username/email, 
        "password": str -> password
    }

    Returns:
        str: data in response['data'], keys are ['login', 'user_id'] OR ['login', 'error']
    """
    data = request.get_json()
    if request.method == "POST" and data:
        username = data["username"]
        password = data["password"]
        
        if(email_validation(username)):
            user = models.User.query.filter_by(email=username).first()
        else:
            user = models.User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            return jsonify(good_response({"login": True, "user_id": user.id, "token": user.get_token()}))
        else:
            return jsonify(bad_response({"login": False, "error": "User doesn't Exist"}))
    else:
        return jsonify(good_response({"login": False, "error": "bad request"}))

@app.route('/api/users', methods=['GET'])
def users() -> str:
    """Gets All Users

    Returns:
        str: data in response['data'], List[Dict[str, Any]]
    """
    all_users = models.User.query.all()
    result = schemas.users_schema.dump(all_users)
    return jsonify(good_response(result))

@app.route('/api/add_user', methods=both_)
def add_user() -> str:
    """Adds a User
    Format:
    data = {
        "username": str -> username, 
        "password": str -> password, 
        "name": str -> name, 
        "date_of_birth": str -> dob <"DD-MM-YYYY">
    }

    Returns:
        str: data in response['data'], keys are ['user_id'] OR ['error']
    """
    data = request.get_json()
    if data and request.method == "POST":
        user = models.User.query.filter_by(username=data['username']).first()
        if user and not user.is_deleted:
            return jsonify(bad_response(({'error': "User Already Exists"})))
        new_user = models.User(
            username=data["username"],
            password=data["password"],
            name=data["name"],
            email=data["email"],
            date_of_birth=data["date_of_birth"],
            is_deleted=False,
        )
        new_user.set_token()
        add(new_user)
        return jsonify(good_response({"user_id": new_user.id, "user_token": new_user.get_token()}))
    else:
        return jsonify(good_response({"error": "bad request"}))

@app.route('/api/user/<user_id>/about/add_about', methods=both_)
def add_about(user_id: int) -> str:
    """Format
    data = {
        "about": str -> about, 
        "token": str -> token
    }

    Args:
        user_id (int): user_id to Change About in

    Returns:
        str: json data in ["data"]
    """
    user = models.User.query.get(user_id)
    data = request.get_json()["about"]
    data_t = request.get_json()["token"]
    if user and data and user.token == data_t:
        user.set_about_user(data)
        return jsonify(good_response(f"about added for user {user.username}"))
    else:
        return jsonify(bad_response({"error": "couldn't add About"}))

@app.route('/api/user/<user_id>/about', methods=both_)
def about(user_id: int) -> str:
    """User About

    Args:
        user_id (int): user_id

    Returns:
        str: data in response['data'], keys are ['username', 'password', 'name', 'posts', 'len_posts', 'comments', 'user_id', 'age']
    """

    user = models.User.query.get(user_id)
    result = schemas.user_schema.dump(user)
    result['stores'] = schemas.stores_schema.dump(user.subbed_stores.all())
    result['len_subbed_stores'] = len(result['stores'])
    return jsonify(good_response(result))

# USER EDIT
@app.route('/api/user/<user_id>/delete', methods=both_)
def delete_user(user_id: int) -> str:
    """Delete A User
    Format
    data = {
        "token": user_token
    }

    Args:
        user_id (int): user_id to Delete User

    Returns:
        str: data in response['data'], keys are ['result']
    """

    user = models.User.query.get(user_id)
    if user and user.get_token() == request.get_json()["token"]:
        user.delete_user()
        db.session.commit()
        return jsonify(good_response({"result": 'User Deleted'}))
    else:
        return jsonify(bad_response({"result": "Error: Token Bad"}))
        # return jsonify(bad_response(result={"error": "token bad"}))

# STORE
@app.route('/api/user/<user_id>/sub_store', methods=['GET', 'POST'])
def add_store_for_user(user_id: int) -> str:
    """Subs a Store For the User 
    Format:
    data = {
        "store_id": int -> store_id to Sub,
        "user_token": str -> user_token,
    }

    Returns:
        str: data in response['data'], keys are ['status']
    """
    data = request.get_json()
    if request.method == "POST" and data:
        user = models.User.query.get(user_id)
        if user and user.get_token() == data["token"]:
            user_sub_check = user.check_subscription()
            if user_sub_check[1] and user.check_for_limit[1]:
                store = models.Store.query.get(data["store_id"])
                user.add_store(store)
                return jsonify(good_response({"post_id": store.id}))
    else:
        return jsonify(bad_response({"error": "bad request"}))

# @app.route('/api/user/<user_id>/view_store/<store_id>', methods=['GET', 'POST'])
# def view_store(user_id: int, store_id: int) -> str:
#     """Views a Post

#     Args:
#         user_id (int): user_id
#         post_id (int): post_id

#     Returns:
#         str: data in response['data'], keys are ['post_title', 'post_id', 'post_body', 'user']
#     """    
#     post_id = post_id
#     post = models.Store.query.get(post_id)
#     if not post.is_deleted:
#         result = schemas.post_schema.dump(post)
#         return jsonify(good_response(result))
#     else:
#         return jsonify(bad_response("[post_deleted]"))

# POST EDITS
@app.route('/api/user/post/<post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id: int) -> str:
    """Delete a Post
    format:
    Data = {
        "user_id": int -> user_id, 
        "token": str-> user_token
    }

    Args:
        post_id (int): post_id to delete

    Returns:
        str: data in response['data'], keys are ['result']
    """
    data = request.get_json()
    user = models.User.query.get(data["user_id"])
    if user and user.get_token() == data["token"]:
        post = models.Posts.query.get(post_id)
        post.delete_post()
        db.session.commit()
        return jsonify(good_response({"result": "Post Deleted"}))

# COMMENTS
@app.route('/api/user/<user_id>/post/add_comment', methods=["GET", "POST"])
def add_comment(user_id: int) -> str:
    """Adds a Comment
    Format:
    data = {
        "post_id": int -> post_id, 
        "comment_body": str -> comment_body, 
        "token": str-> user_token
    }
    
    Args:
        user_id (int): user_id

    Returns:
        str: data in response['data'], keys are ['comment_id', 'post_id'] OR ['error']
    """    
    data = request.get_json()
    if request.method == "POST" and data:
        user = models.User.query.get(user_id)
        if user.get_token() == data['token']:
            if not models.Posts.query.get(data["post_id"]).first().is_deleted:
                comment = models.Comments(
                    comment_body=data["comment_body"],
                    comment_by_user=user,
                    comment_post=models.Posts.query.get(data["post_id"]),
                )
                add(comment)
                return jsonify(good_response({"comment_id": comment.id, "post_id": data["post_id"]}))

# Edit Comments
@app.route('/api/user/<user_id>/comment/<comment_id>/delete', methods=['GET',"POST"])
def delete_comment(user_id: int, comment_id: int) -> str:
    """Deletes a User Comment
    data = {
        "token": str -> user_token
    }

    Args:
        user_id (int): user_id
        comment_id (int): comment_id

    Returns:
        str: data in response['data'], keys are ['result']
    """
    data = request.get_json()
    user = models.User.query.get(user_id)
    if user and user.get_token() == data["token"]:
        comment = models.Comments.query.get(comment_id)
        comment.delete_comment()
        db.session.commit()
        return jsonify(good_response({"result": "Post Deleted"}))

# OTHER Methods
def email_validation(email):
    if fullmatch(email_re, email):
      return True
    else:
      return False
def delete(object):
    db.session.delete(object)
    db.session.commit()
def add(object):
    db.session.add(object)
    db.session.commit()
def good_response(data: Any):
    return {'response': "good", 'data': data}
def bad_response(data: Any):
    return {'response': "bad", 'data': data}
