from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from models import db, Product

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def ensure_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route("/products")
@login_required
def products():
    ensure_admin()
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin_products.html", products=products)

@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
def new_product():
    ensure_admin()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price", "0"))
        image_url = request.form.get("image_url")
        stock = int(request.form.get("stock", "0"))
        category = request.form.get("category")
        product = Product(name=name, description=description, price=price, image_url=image_url, stock=stock, category=category)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("admin.products"))
    return render_template("admin_product_form.html", product=None)

@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    ensure_admin()
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = float(request.form.get("price", "0"))
        product.image_url = request.form.get("image_url")
        product.stock = int(request.form.get("stock", "0"))
        product.category = request.form.get("category")
        db.session.commit()
        return redirect(url_for("admin.products"))
    return render_template("admin_product_form.html", product=product)

@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    ensure_admin()
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin.products"))
