import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


#db_drop_and_create_all()


def short(getting_drinks):
    drinks = [drink.short() for drink in getting_drinks]
    return drinks

def long(getting_drinks):
    drinks = [drink.long() for drink in getting_drinks]
    return drinks


# ROUTES

@app.route('/drinks')
def get_drinks():
    getting_drinks = Drink.query.order_by(Drink.id).all()
    drinks = short(getting_drinks)
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        "success": True, 
        "drinks": drinks
        }), 200


@requires_auth('get:drinks-detail')
@app.route('/drinks-detail')
def drinks_details():
    getting_drinks = Drink.query.order_by(Drink.id).all()
    drinks = long(getting_drinks)
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        "success": True, 
        "drinks": drinks
        }), 200


@requires_auth('post:drinks')
@app.route('/drinks', methods=["POST"])
def create_drink():
    body = request.get_json()
    new_title = body.get("title")
    new_recipe = body.get("recipe")
    try:
        drink = Drink(title=new_title,recipe=new_recipe)
        drink.insert()
        drink = long(drink)
        return jsonify({
        "success": True, 
        "drinks": drink
        }), 200
    except:
        abort(422)


@requires_auth('patch:drinks')
@app.route('/drinks/<id>', methods=["PATCH"])
def edit_drink():
    body = request.get_json()
    new_title = body.get("title")
    new_recipe = body.get("recipe")
    try:
        getting_drink = Drink.query.filter(Drink.id == id).one_or_none()
        if getting_drink is None:
            abort(404)
        getting_drink.title = new_title
        getting_drink.recipe = new_recipe
        getting_drink.update()
        getting_drink = long(getting_drink)
        return jsonify({
            "success": True, 
            "drinks": getting_drink
            }), 200
    except:
        abort(400)
    

@requires_auth('delete:drinks')
@app.route('/drinks/<id>', methods=["DELETE"])
def delete_drink():
    try:
        getting_drink = Drink.query.filter(Drink.id == id).one_or_none()
        if getting_drink is None:
            abort(404)
        getting_drink.delete()
        return jsonify({
            "success": True, 
            "delete": id
            }), 200
    except:
        abort(400)

# Error Handling



@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)  
def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code