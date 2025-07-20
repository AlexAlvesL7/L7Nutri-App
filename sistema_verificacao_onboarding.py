#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISTEMA DE VERIFICAÇÃO DE EMAIL E ONBOARDING
Implementa verificação de email obrigatória e questionário inicial
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import re
from datetime import datetime, timedelta
import requests
import os

# Configurações de Email
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'EMAIL_USER': os.getenv('EMAIL_USER', 'seu_email@gmail.com'),
    'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD', 'sua_senha_app'),
    'FROM_EMAIL': 'noreply@l7nutri.com',
    'FROM_NAME': 'L7Nutri - Nutrição Inteligente'
}

def validar_email_real(email):
    """Valida se o email é válido e se o domínio existe"""
    
    # Validação básica de formato
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    # Lista de domínios temporários/descartáveis para bloquear
    dominios_bloqueados = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'temp-mail.org'
    ]
    
    dominio = email.split('@')[1].lower()
    if dominio in dominios_bloqueados:
        return False, "Emails temporários não são permitidos"
    
    # Verificar se é um domínio comum válido
    dominios_validos = [
        'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
        'bol.com.br', 'uol.com.br', 'ig.com.br', 'terra.com.br'
    ]
    
    if dominio not in dominios_validos:
        # Para domínios não conhecidos, fazer verificação básica
        try:
            import socket
            socket.gethostbyname(dominio)
        except:
            return False, "Domínio de email não encontrado"
    
    return True, "Email válido"

def gerar_token_verificacao():
    """Gera token único para verificação de email"""
    return secrets.token_urlsafe(32)

def enviar_email_verificacao(email, nome, token):
    """Envia email de verificação de conta"""
    
    try:
        # URL de verificação
        url_verificacao = f"https://l7nutri-app.onrender.com/verificar-email?token={token}"
        
        # HTML do email
        html_email = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Confirme sua conta L7Nutri</title>
        </head>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🥗 L7Nutri</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Nutrição Inteligente com IA</p>
                </div>
                
                <!-- Conteúdo -->
                <div style="padding: 30px;">
                    <h2 style="color: #333; margin-bottom: 20px;">Olá, {nome}! 👋</h2>
                    
                    <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                        Bem-vindo(a) à <strong>L7Nutri</strong>! Estamos muito felizes em tê-lo(a) conosco.
                    </p>
                    
                    <p style="color: #666; line-height: 1.6; margin-bottom: 25px;">
                        Para garantir a segurança da sua conta e ativar todos os recursos, 
                        clique no botão abaixo para confirmar seu email:
                    </p>
                    
                    <!-- Botão de Verificação -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{url_verificacao}" 
                           style="background: linear-gradient(135deg, #28a745, #20c997); 
                                  color: white; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 25px; 
                                  font-weight: bold; 
                                  font-size: 16px;
                                  display: inline-block;
                                  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);">
                            ✅ Confirmar Minha Conta
                        </a>
                    </div>
                    
                    <!-- Informações Importantes -->
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin: 25px 0;">
                        <h3 style="color: #28a745; margin: 0 0 10px 0; font-size: 16px;">🎯 Próximos Passos:</h3>
                        <ul style="color: #666; margin: 0; padding-left: 20px;">
                            <li>Confirme seu email clicando no botão acima</li>
                            <li>Complete o questionário de saúde da L7Chef</li>
                            <li>Receba seu plano nutricional personalizado</li>
                            <li>Comece sua jornada de transformação!</li>
                        </ul>
                    </div>
                    
                    <!-- Link alternativo -->
                    <p style="color: #999; font-size: 14px; line-height: 1.5; margin-top: 25px;">
                        <strong>Não consegue clicar no botão?</strong><br>
                        Copie e cole este link no seu navegador:<br>
                        <span style="color: #667eea; word-break: break-all;">{url_verificacao}</span>
                    </p>
                    
                    <!-- Aviso de Segurança -->
                    <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 25px 0;">
                        <p style="color: #856404; margin: 0; font-size: 14px;">
                            🔒 <strong>Segurança:</strong> Este link expira em 24 horas. 
                            Se você não criou esta conta, ignore este email.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                    <p style="color: #999; margin: 0; font-size: 14px;">
                        © 2025 L7Nutri - Transforme sua relação com a alimentação
                    </p>
                    <p style="color: #999; margin: 5px 0 0 0; font-size: 12px;">
                        Este é um email automático, não responda.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Configurar email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🥗 Confirme sua conta L7Nutri - Bem-vindo!"
        msg['From'] = f"{EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['FROM_EMAIL']}>"
        msg['To'] = email
        
        # Anexar HTML
        html_part = MIMEText(html_email, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Enviar email
        with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['EMAIL_USER'], EMAIL_CONFIG['EMAIL_PASSWORD'])
            server.send_message(msg)
        
        print(f"✅ Email de verificação enviado para: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

def criar_usuario_com_verificacao(dados_usuario):
    """Cria usuário com status 'pendente' aguardando verificação"""
    
    # Validar email
    email_valido, mensagem = validar_email_real(dados_usuario['email'])
    if not email_valido:
        return False, mensagem
    
    # Gerar token de verificação
    token = gerar_token_verificacao()
    
    # Dados do usuário com status pendente
    usuario_pendente = {
        **dados_usuario,
        'status': 'pendente_verificacao',
        'token_verificacao': token,
        'data_criacao': datetime.now(),
        'token_expira': datetime.now() + timedelta(hours=24),
        'onboarding_completo': False
    }
    
    # Salvar no banco (status pendente)
    # TODO: Implementar salvamento no banco
    
    # Enviar email de verificação
    sucesso_email = enviar_email_verificacao(
        dados_usuario['email'], 
        dados_usuario['nome'], 
        token
    )
    
    if sucesso_email:
        return True, "Conta criada! Verifique seu email para ativar."
    else:
        return False, "Erro ao enviar email de verificação"

# Questionário L7Chef para onboarding obrigatório
QUESTIONARIO_L7CHEF = {
    "etapa_1_dados_pessoais": {
        "titulo": "📊 Dados Pessoais",
        "campos": [
            {"nome": "idade", "tipo": "number", "label": "Idade", "obrigatorio": True},
            {"nome": "sexo", "tipo": "select", "label": "Sexo", "opcoes": ["Masculino", "Feminino"], "obrigatorio": True},
            {"nome": "peso_atual", "tipo": "number", "label": "Peso Atual (kg)", "obrigatorio": True},
            {"nome": "altura", "tipo": "number", "label": "Altura (cm)", "obrigatorio": True},
            {"nome": "peso_meta", "tipo": "number", "label": "Peso Desejado (kg)", "obrigatorio": True}
        ]
    },
    
    "etapa_2_estilo_vida": {
        "titulo": "🏃‍♀️ Estilo de Vida",
        "campos": [
            {
                "nome": "nivel_atividade", 
                "tipo": "select", 
                "label": "Nível de Atividade Física",
                "opcoes": [
                    "Sedentário (pouco ou nenhum exercício)",
                    "Levemente ativo (exercício leve 1-3 dias/semana)",
                    "Moderadamente ativo (exercício moderado 3-5 dias/semana)",
                    "Muito ativo (exercício intenso 6-7 dias/semana)",
                    "Extremamente ativo (exercício muito intenso, trabalho físico)"
                ],
                "obrigatorio": True
            },
            {
                "nome": "objetivo_principal",
                "tipo": "select",
                "label": "Objetivo Principal",
                "opcoes": [
                    "Perder peso",
                    "Ganhar massa muscular",
                    "Manter peso atual",
                    "Melhorar saúde geral",
                    "Aumentar energia",
                    "Melhorar performance esportiva"
                ],
                "obrigatorio": True
            },
            {"nome": "horas_sono", "tipo": "number", "label": "Horas de sono por noite", "obrigatorio": True},
            {"nome": "nivel_stress", "tipo": "select", "label": "Nível de Stress", "opcoes": ["Baixo", "Médio", "Alto"], "obrigatorio": True}
        ]
    },
    
    "etapa_3_alimentacao": {
        "titulo": "🍽️ Hábitos Alimentares",
        "campos": [
            {"nome": "refeicoes_dia", "tipo": "number", "label": "Quantas refeições faz por dia?", "obrigatorio": True},
            {"nome": "agua_diaria", "tipo": "number", "label": "Litros de água por dia", "obrigatorio": True},
            {
                "nome": "restricoes_alimentares",
                "tipo": "checkbox",
                "label": "Restrições Alimentares",
                "opcoes": [
                    "Vegetariano", "Vegano", "Intolerância à lactose", 
                    "Diabético", "Hipertensão", "Colesterol alto",
                    "Alergia a glúten", "Nenhuma"
                ],
                "obrigatorio": False
            },
            {
                "nome": "alimentos_favoritos",
                "tipo": "checkbox",
                "label": "Alimentos Favoritos",
                "opcoes": [
                    "Frutas", "Verduras", "Carnes", "Peixes", "Ovos",
                    "Massas", "Arroz", "Feijão", "Nozes", "Iogurte"
                ],
                "obrigatorio": False
            }
        ]
    },
    
    "etapa_4_saude": {
        "titulo": "🏥 Informações de Saúde",
        "campos": [
            {"nome": "problemas_saude", "tipo": "textarea", "label": "Problemas de saúde ou medicamentos", "obrigatorio": False},
            {"nome": "historico_dietas", "tipo": "textarea", "label": "Já fez alguma dieta? Qual resultado?", "obrigatorio": False},
            {"nome": "frequencia_exercicio", "tipo": "select", "label": "Com que frequência se exercita?", 
             "opcoes": ["Nunca", "1x/semana", "2-3x/semana", "4-5x/semana", "Todos os dias"], "obrigatorio": True},
            {"nome": "motivacao", "tipo": "textarea", "label": "O que mais te motiva a cuidar da alimentação?", "obrigatorio": True}
        ]
    }
}

def analisar_questionario_l7chef(respostas):
    """Analisa respostas do questionário e gera recomendações personalizadas"""
    
    # Calcular TMB (Taxa Metabólica Basal)
    peso = float(respostas['peso_atual'])
    altura = float(respostas['altura'])
    idade = int(respostas['idade'])
    sexo = respostas['sexo']
    
    if sexo.lower() == 'masculino':
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
    
    # Fator de atividade
    fatores_atividade = {
        "Sedentário (pouco ou nenhum exercício)": 1.2,
        "Levemente ativo (exercício leve 1-3 dias/semana)": 1.375,
        "Moderadamente ativo (exercício moderado 3-5 dias/semana)": 1.55,
        "Muito ativo (exercício intenso 6-7 dias/semana)": 1.725,
        "Extremamente ativo (exercício muito intenso, trabalho físico)": 1.9
    }
    
    fator = fatores_atividade.get(respostas['nivel_atividade'], 1.55)
    calorias_manutencao = tmb * fator
    
    # Ajustar por objetivo
    objetivo = respostas['objetivo_principal']
    if 'Perder peso' in objetivo:
        calorias_meta = calorias_manutencao - 500
        proteina_pct = 30  # Maior proteína para preservar massa
        carbo_pct = 40
        gordura_pct = 30
    elif 'Ganhar massa' in objetivo:
        calorias_meta = calorias_manutencao + 300
        proteina_pct = 25
        carbo_pct = 50  # Mais carboidratos para energia
        gordura_pct = 25
    else:  # Manter peso
        calorias_meta = calorias_manutencao
        proteina_pct = 25
        carbo_pct = 45
        gordura_pct = 30
    
    # Calcular macros
    proteina_g = (calorias_meta * proteina_pct / 100) / 4
    carbo_g = (calorias_meta * carbo_pct / 100) / 4
    gordura_g = (calorias_meta * gordura_pct / 100) / 9
    
    # Recomendações personalizadas
    recomendacoes = {
        "calorias_diarias": round(calorias_meta),
        "macronutrientes": {
            "proteina": round(proteina_g),
            "carboidrato": round(carbo_g),
            "gordura": round(gordura_g)
        },
        "agua_recomendada": max(2.5, peso * 0.035),  # 35ml por kg
        "refeicoes_sugeridas": 5 if objetivo == "Ganhar massa muscular" else 4,
        "dicas_personalizadas": gerar_dicas_personalizadas(respostas)
    }
    
    return recomendacoes

def gerar_dicas_personalizadas(respostas):
    """Gera dicas baseadas nas respostas do usuário"""
    
    dicas = []
    
    # Dicas baseadas no objetivo
    if 'Perder peso' in respostas['objetivo_principal']:
        dicas.extend([
            "🔥 Foque em alimentos com alta saciedade: proteínas magras e fibras",
            "⏰ Faça 4-5 refeições menores ao longo do dia",
            "💧 Beba água antes das refeições para aumentar a saciedade"
        ])
    
    # Dicas baseadas na atividade física
    if 'Sedentário' in respostas['nivel_atividade']:
        dicas.append("🚶‍♀️ Comece com caminhadas de 20 minutos diários")
    
    # Dicas baseadas no sono
    if int(respostas['horas_sono']) < 7:
        dicas.append("😴 Durma pelo menos 7-8 horas para otimizar o metabolismo")
    
    # Dicas baseadas no stress
    if respostas['nivel_stress'] == 'Alto':
        dicas.append("🧘‍♀️ Pratique técnicas de relaxamento antes das refeições")
    
    return dicas

if __name__ == "__main__":
    print("🔧 Sistema de Verificação de Email e Onboarding configurado!")
    print("📧 Configurações de email prontas")
    print("📋 Questionário L7Chef implementado")
    print("🎯 Sistema de recomendações personalizado")
