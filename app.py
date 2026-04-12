from flask import Flask
from models.db import init_db

app = Flask(__name__)
app.secret_key = 'salao_beleza_secret_2024'

init_db(app)

from routes.auth import auth_bp
from routes.agendamento import agendamento_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(agendamento_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)