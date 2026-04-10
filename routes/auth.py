from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models.models import Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.senha, senha):
            session['admin_id'] = admin.id
            return redirect(url_for('admin.painel'))
        flash('Usuário ou senha incorretos.')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('agendamento.index'))