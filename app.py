from flask import Flask
from models.db import init_db
import schedule
import time
from utils.lembrete import buscar_agendamentos_amanha

app = Flask(__name__)
app.secret_key = 'salao_beleza_secret_2024'

init_db(app)

from routes.auth import auth_bp
from routes.agendamento import agendamento_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(agendamento_bp)
app.register_blueprint(admin_bp)

def start_scheduler():
    schedule.every().day.at("09:00").do(buscar_agendamentos_amanha)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    import threading
    threading.Thread(target=start_scheduler).start()
    app.run(debug=True)