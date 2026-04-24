from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.db import db
from models.models import Agendamento, Horario, Servico, DiaSemana, DataBloqueada
from datetime import date, datetime
import urllib.parse

agendamento_bp = Blueprint('agendamento', __name__)

WHATSAPP_DONA = '5519996733248'

@agendamento_bp.route('/')
def index():
    servicos = Servico.query.filter_by(ativo=True).all()
    hoje = date.today().isoformat()

    # Dias da semana ativos (0=seg ... 6=dom) para bloquear no calendário via JS
    dias_ativos = [d.dia for d in DiaSemana.query.filter_by(ativo=True).all()]

    # Datas bloqueadas para bloquear no calendário via JS
    datas_bloqueadas = [d.data for d in DataBloqueada.query.all()]

    return render_template('index.html',
        servicos=servicos,
        hoje=hoje,
        dias_ativos=dias_ativos,
        datas_bloqueadas=datas_bloqueadas
    )

@agendamento_bp.route('/horarios-disponiveis')
def horarios_disponiveis():
    data = request.args.get('data')
    if not data:
        return jsonify([])

    # Verifica se o dia da semana está ativo
    dia_semana = datetime.strptime(data, '%Y-%m-%d').weekday()  # 0=seg, 6=dom
    dia_obj = DiaSemana.query.filter_by(dia=dia_semana).first()
    if not dia_obj or not dia_obj.ativo:
        return jsonify([])

    # Verifica se a data está bloqueada
    if DataBloqueada.query.filter_by(data=data).first():
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

    # Verifica se cliente está bloqueado
    bloqueado = Agendamento.query.filter_by(telefone=telefone, bloqueado=1).first()
    if bloqueado:
        flash('Você possui pendência por falta. Entre em contato para liberar novo agendamento.')
        return redirect('/')

    existente = Agendamento.query.filter_by(data=data, hora=hora).first()
    if existente:
        flash('Este horário já foi reservado. Escolha outro.')
        return redirect(url_for('agendamento.index'))

    servico = Servico.query.get(servico_id)
    ag = Agendamento(nome=nome, telefone=telefone, servico_id=servico_id, data=data, hora=hora, compareceu=0, bloqueado=0)
    db.session.add(ag)
    db.session.commit()

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