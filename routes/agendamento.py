from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.db import db
from models.models import Agendamento, Horario, Servico
from datetime import date
import urllib.parse

agendamento_bp = Blueprint('agendamento', __name__)

# Número da dona (somente dígitos, com DDI)
WHATSAPP_DONA = '5519996733248'

@agendamento_bp.route('/')
def index():
    servicos = Servico.query.filter_by(ativo=True).all()
    hoje = date.today().isoformat()
    return render_template('index.html', servicos=servicos, hoje=hoje)

@agendamento_bp.route('/horarios-disponiveis')
def horarios_disponiveis():
    data = request.args.get('data')
    if not data:
        return jsonify([])
    horarios_ativos = Horario.query.filter_by(ativo=True).order_by(Horario.hora).all()
    agendados = [a.hora for a in Agendamento.query.filter_by(data=data).all()]
    disponiveis = [h.hora for h in horarios_ativos if h.hora not in agendados]
    return jsonify(disponiveis)

@agendamento_bp.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    servico_id = request.form.get('servico_id')
    data = request.form.get('data')
    hora = request.form.get('hora')

    if not all([nome, telefone, servico_id, data, hora]):
        flash('Preencha todos os campos.')
        return redirect(url_for('agendamento.index'))

    existente = Agendamento.query.filter_by(data=data, hora=hora).first()
    if existente:
        flash('Este horário já foi reservado. Escolha outro.')
        return redirect(url_for('agendamento.index'))

    servico = Servico.query.get(servico_id)
    ag = Agendamento(nome=nome, telefone=telefone, servico_id=servico_id, data=data, hora=hora)
    db.session.add(ag)
    db.session.commit()

    # Monta o link do WhatsApp para a dona
    mensagem = (
        f"📅 *Novo Agendamento — Lu Cabelereira*\n\n"
        f"👤 *Nome:* {nome}\n"
        f"📱 *Telefone:* {telefone}\n"
        f"💅 *Serviço:* {servico.nome}\n"
        f"📆 *Data:* {data}\n"
        f"🕐 *Horário:* {hora}\n\n"
        f"_Agendamento realizado pelo site._"
    )
    whatsapp_url = f"https://wa.me/{WHATSAPP_DONA}?text={urllib.parse.quote(mensagem)}"

    return render_template('sucesso.html',
        nome=nome,
        servico=servico.nome,
        data=data,
        hora=hora,
        whatsapp_url=whatsapp_url
    )