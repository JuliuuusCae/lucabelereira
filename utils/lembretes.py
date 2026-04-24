from datetime import datetime, timedelta
from models.db import db, Agendamento

def buscar_agendamentos_amanha():
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    agendamentos = Agendamento.query.filter_by(data=amanha).all()

    for ag in agendamentos:
        mensagem = f"""
Olá {ag.nome} 💅

Lembrando do seu horário amanhã às {ag.hora}.

Caso não possa comparecer, avise com antecedência 😉

Lú Manicure
        """

        print(f"Enviar para {ag.telefone}: {mensagem}")

        # aqui depois você integra com WhatsApp API