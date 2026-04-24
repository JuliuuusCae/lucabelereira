from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import db
from models.models import Agendamento, Horario, Servico, DiaSemana, DataBloqueada
from functools import wraps

admin_bp = Blueprint('admin', __name__)

NOMES_DIAS = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

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
    dias_semana = DiaSemana.query.order_by(DiaSemana.dia).all()
    datas_bloqueadas = DataBloqueada.query.order_by(DataBloqueada.data).all()
    return render_template('admin.html',
        agendamentos=agendamentos,
        horarios=horarios,
        servicos=servicos,
        dias_semana=dias_semana,
        datas_bloqueadas=datas_bloqueadas,
        nomes_dias=NOMES_DIAS
    )

# ── HORÁRIOS ──────────────────────────────────────────────
@admin_bp.route('/admin/horario/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_horario(id):
    h = Horario.query.get_or_404(id)
    h.ativo = not h.ativo
    db.session.commit()
    flash('Horário atualizado.')
    return redirect(url_for('admin.painel') + '#horarios')

@admin_bp.route('/admin/horario/add', methods=['POST'])
@login_required
def add_horario():
    hora = request.form.get('nova_hora', '').strip()
    if hora:
        if not Horario.query.filter_by(hora=hora).first():
            db.session.add(Horario(hora=hora, ativo=True))
            db.session.commit()
            flash('Horário adicionado.')
        else:
            flash('Horário já existe.')
    return redirect(url_for('admin.painel') + '#horarios')

@admin_bp.route('/admin/horario/delete/<int:id>', methods=['POST'])
@login_required
def delete_horario(id):
    h = Horario.query.get_or_404(id)
    db.session.delete(h)
    db.session.commit()
    flash('Horário removido.')
    return redirect(url_for('admin.painel') + '#horarios')

# ── SERVIÇOS ──────────────────────────────────────────────
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
    return redirect(url_for('admin.painel') + '#servicos')

# ── AGENDAMENTOS ──────────────────────────────────────────
@admin_bp.route('/admin/agendamento/delete/<int:id>', methods=['POST'])
@login_required
def delete_agendamento(id):
    ag = Agendamento.query.get_or_404(id)
    db.session.delete(ag)
    db.session.commit()
    flash('Agendamento removido.')
    return redirect(url_for('admin.painel') + '#agendamentos')

@admin_bp.route('/admin/agendamento/falta/<int:id>', methods=['POST'])
@login_required
def marcar_falta(id):
    ag = Agendamento.query.get_or_404(id)
    ag.compareceu = 0
    ag.bloqueado = 1
    db.session.commit()
    flash('Cliente marcado como falta e bloqueado.')
    return redirect(url_for('admin.painel') + '#agendamentos')

@admin_bp.route('/admin/agendamento/desbloquear/<int:id>', methods=['POST'])
@login_required
def desbloquear(id):
    ag = Agendamento.query.get_or_404(id)
    ag.bloqueado = 0
    db.session.commit()
    flash('Cliente desbloqueado.')
    return redirect(url_for('admin.painel') + '#agendamentos')

# ── DIAS DA SEMANA ────────────────────────────────────────
@admin_bp.route('/admin/dia/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_dia(id):
    d = DiaSemana.query.get_or_404(id)
    d.ativo = not d.ativo
    db.session.commit()
    flash('Dia de atendimento atualizado.')
    return redirect(url_for('admin.painel') + '#disponibilidade')

# ── DATAS BLOQUEADAS ──────────────────────────────────────
@admin_bp.route('/admin/data-bloqueada/add', methods=['POST'])
@login_required
def add_data_bloqueada():
    data = request.form.get('data_bloquear', '').strip()
    motivo = request.form.get('motivo', '').strip()
    if data:
        if not DataBloqueada.query.filter_by(data=data).first():
            db.session.add(DataBloqueada(data=data, motivo=motivo or None))
            db.session.commit()
            flash(f'Data {data} bloqueada.')
        else:
            flash('Esta data já está bloqueada.')
    return redirect(url_for('admin.painel') + '#disponibilidade')

@admin_bp.route('/admin/data-bloqueada/delete/<int:id>', methods=['POST'])
@login_required
def delete_data_bloqueada(id):
    d = DataBloqueada.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash('Data desbloqueada.')
    return redirect(url_for('admin.painel') + '#disponibilidade')