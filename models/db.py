from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3

db = SQLAlchemy()

def init_db(app):
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        from models.models import Agendamento, Horario, Servico, Admin, DiaSemana, DataBloqueada
        db.create_all()
        _migrar_colunas(db_path)
        _seed_data()

def _migrar_colunas(db_path):
    """Adiciona colunas novas se não existirem no banco antigo."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verifica colunas existentes na tabela agendamentos
    cursor.execute("PRAGMA table_info(agendamentos)")
    colunas = [row[1] for row in cursor.fetchall()]

    if 'compareceu' not in colunas:
        cursor.execute("ALTER TABLE agendamentos ADD COLUMN compareceu INTEGER DEFAULT 0")

    if 'bloqueado' not in colunas:
        cursor.execute("ALTER TABLE agendamentos ADD COLUMN bloqueado INTEGER DEFAULT 0")

    conn.commit()
    conn.close()

def _seed_data():
    from models.models import Servico, Horario, Admin, DiaSemana
    from werkzeug.security import generate_password_hash

    if not Servico.query.first():
        servicos = [
            ('Progressiva', 'a partir de 170,00'),
            ('Pé e Mão', '60,00'),
            ('Pé', '40,00'),
            ('Mão', '30,00'),
            ('Selante', 'a partir de 150,00'),
            ('Coloração', 'a partir de 150,00'),
            ('Luzes', 'a partir de 200,00'),
            ('Definitiva', 'a partir de 250,00'),
            ('Sobrancelha com Hena', '40,00'),
            ('Sobrancelha sem Hena', '30,00'),
            ('Plástica dos Pés', '90,00'),
            ('Pacote de Hidratação Capilar', '130,00'),
            ('Pacote de Escova Capilar', '110,00'),
            ('Pacote 2 Hidratação e 2 Escova', '220,00'),
            ('Pacote de Unha 2 Pé e 4 Mão', '160,00'),
            ('Escova e Chapa', '80,00'),
            ('Corte de Cabelo', 'a partir de 60,00'),
            ('Hidratação', 'a partir de 70,00'),
        ]
        for nome, preco in servicos:
            db.session.add(Servico(nome=nome, preco=preco))

    if not Horario.query.first():
        horarios = ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']
        for h in horarios:
            db.session.add(Horario(hora=h, ativo=True))

    if not Admin.query.first():
        admin = Admin(username='admin', senha=generate_password_hash('admin123'))
        db.session.add(admin)

    if not DiaSemana.query.first():
        for i in range(7):
            db.session.add(DiaSemana(dia=i, ativo=(i != 6)))

    db.session.commit()
