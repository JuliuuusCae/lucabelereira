from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import db
from models.models import Agendamento, Horario, Servico
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin')
@login_required
def painel():
    agendamentos = Agendamento.query.order_by(Agendamento.data, Agendamento.hora).all()
    horarios = Horario.query.order_by(Horario.hora).all()
    servicos = Servico.query.order_by(Servico.nome).all()
    return render_template('admin.html', agendamentos=agendamentos, horarios=horarios, servicos=servicos)

@admin_bp.route('/admin/horario/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_horario(id):
    h = Horario.query.get_or_404(id)
    h.ativo = not h.ativo
    db.session.commit()
    flash('Horário atualizado.')
    return redirect(url_for('admin.painel'))

@admin_bp.route('/admin/horario/add', methods=['POST'])
@login_required
def add_horario():
    hora = request.form.get('nova_hora', '').strip()
    if hora:
        existente = Horario.query.filter_by(hora=hora).first()
        if not existente:
            db.session.add(Horario(hora=hora, ativo=True))
            db.session.commit()
            flash('Horário adicionado.')
        else:
            flash('Horário já existe.')
    return redirect(url_for('admin.painel'))

@admin_bp.route('/admin/horario/delete/<int:id>', methods=['POST'])
@login_required
def delete_horario(id):
    h = Horario.query.get_or_404(id)
    db.session.delete(h)
    db.session.commit()
    flash('Horário removido.')
    return redirect(url_for('admin.painel'))

@admin_bp.route('/admin/servico/preco/<int:id>', methods=['POST'])
@login_required
def update_preco(id):
    s = Servico.query.get_or_404(id)
    novo_preco = request.form.get('preco', '').strip()
    if novo_preco:
        s.preco = novo_preco
        db.session.commit()
        flash(f'Preço de "{s.nome}" atualizado.')
    else:
        flash('Valor não pode ser vazio.')
    return redirect(url_for('admin.painel'))

@admin_bp.route('/admin/agendamento/delete/<int:id>', methods=['POST'])
@login_required
def delete_agendamento(id):
    ag = Agendamento.query.get_or_404(id)
    db.session.delete(ag)
    db.session.commit()
    flash('Agendamento removido.')
    return redirect(url_for('admin.painel'))