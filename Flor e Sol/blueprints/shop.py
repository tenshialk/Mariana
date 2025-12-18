from flask import Blueprint, render_template, request
from models import Product, db

shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    products = Product.query
    if q:
        products = products.filter(Product.name.ilike(f"%{q}%"))
    products = products.order_by(Product.id.desc()).all()
    return render_template("index.html", products=products, q=q)

@shop_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)
