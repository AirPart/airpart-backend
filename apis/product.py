"""Apis products for managing for product action"""

from flask import Blueprint, request

from db import JsonDB
from env import getenv
from product import Action, Product

envs = getenv()
db = JsonDB(envs.get("DB_ADDRESS"))
action = Action(db)

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["GET"])
def get_all_products():
    """Load all products from database"""
    if request.method == "GET":
        products = action.getallproduct()
        if products:
            return {
                "data": products,
                "messege": "success",
            }
        return {
            "data": products,
            "message": "db is empty",
        }


@product_bp.route("/product/<id>", methods=["GET"])
def get_a_product(id: str) -> dict:
    """Load detail a product from database"""
    if request.method == "GET":
        product = action.getaproduct(id)
        if product:
            return {
                "data": product,
                "messege": "success",
            }
        return {
            "data": product,
            "message": f"not exists product with this {id} id",
        }


@product_bp.route("/product/add/<portnumber>&<name>&<total>", methods=["POST"])
def productadd(portnumber, name, total) -> dict:
    """Add a product in database"""
    if request.method == "POST":
        product = Product(portnumber=portnumber, name=name, total=total)
        action.addproduct(product)
        return {"messege": "success"}


@product_bp.route("/product/delete/<id>", methods=["DELETE"])
def removeproduct(id: str) -> dict:
    """Delete a product from database"""
    if request.method == "DELETE":
        product = action.getaproduct(id)
        if product:
            action.rmproduct(id)
            return {"messege": "success"}
        return {
            "data": product,
            "message": f"not exists product with this {id} id",
        }


@product_bp.route("/product/edit/<id>&<portnumber>&<name>&<total>", methods=["PUT"])
def editproduct(id, portnumber, name, total) -> dict:
    """Edit a product in database with id"""
    if request.method == "PUT":
        product = action.getaproduct(id)
        if product:
            newproduct = Product(portnumber=portnumber, name=name, total=total)
            action.putproduct(id, newproduct)
            return {"messege": "success"}
        return {
            "data": product,
            "message": f"not exists product with this {id} id",
        }
