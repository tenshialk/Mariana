from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user
from models import db, Product, CartItem, Order, OrderItem

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")

@cart_bp.route("/")
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    products = {p.id: p for p in Product.query.filter(Product.id.in_([i.product_id for i in items])).all()} if items else {}
    total = sum(i.quantity * products[i.product_id].price for i in items) if items else 0.0
    return render_template("cart.html", items=items, products=products, total=total)

@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", "1"))
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    flash("Item adicionado ao carrinho.")
    return redirect(url_for("shop.product_detail", product_id=product.id))

@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return redirect(url_for("cart.view_cart"))
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        return redirect(url_for("cart.view_cart"))
    total = 0.0
    for i in items:
        product = Product.query.get(i.product_id)
        if i.quantity > product.stock:
            flash("Estoque insuficiente.")
            return redirect(url_for("cart.view_cart"))
        total += i.quantity * product.price
    order = Order(user_id=current_user.id, total=total)
    db.session.add(order)
    db.session.flush()
    for i in items:
        product = Product.query.get(i.product_id)
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=i.quantity, unit_price=product.price)
        db.session.add(order_item)
        product.stock -= i.quantity
        db.session.delete(i)
    db.session.commit()
    return render_template("order_success.html", order=order)
