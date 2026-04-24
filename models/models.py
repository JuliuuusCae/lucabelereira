from models.db import db
from datetime import datetime

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    compareceu = db.Column(db.Integer, default=0)
    bloqueado = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    servico = db.relationship('Servico', backref='agendamentos')

class Horario(db.Model):
    __tablename__ = 'horarios'
    id = db.Column(db.Integer, primary_key=True)
    hora = db.Column(db.String(5), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)

class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, default=True)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class DiaSemana(db.Model):
    __tablename__ = 'dias_semana'
    id = db.Column(db.Integer, primary_key=True)
    # 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
    dia = db.Column(db.Integer, nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)

class DataBloqueada(db.Model):
    __tablename__ = 'datas_bloqueadas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10), nullable=False, unique=True)
    motivo = db.Column(db.String(100), nullable=True)