import os
from flask import Flask
from flask_login import LoginManager
from models import db, User
from blueprints.auth import auth_bp
from blueprints.shop import shop_bp
from blueprints.cart import cart_bp
from blueprints.admin import admin_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(admin_bp)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
