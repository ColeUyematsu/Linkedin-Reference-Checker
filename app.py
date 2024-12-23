from flask import Flask
from flask_migrate import Migrate  # Import Flask-Migrate
from models import db, bcrypt, login_manager
from routes import main

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)  # Add this line to integrate Migrate


with app.app_context():
    db.create_all()  # Creates the database tables

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)