#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar tabelas MySQL no Hostinger
"""

import os
import pymysql
from app import app, db

def criar_tabelas():
    """
    Cria as tabelas no banco MySQL usando SQLAlchemy
    """
    print("CRIANDO TABELAS NO MYSQL...")
    
    # Forcar modo producao
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            print("TABELAS CRIADAS COM SUCESSO!")
            
            # Listar tabelas criadas
            result = db.engine.execute("SHOW TABLES")
            tabelas = [row[0] for row in result]
            
            print(f"\nTABELAS ENCONTRADAS ({len(tabelas)}):")
            for i, tabela in enumerate(tabelas, 1):
                print(f"  {i}. {tabela}")
                
                # Mostrar estrutura da tabela
                result = db.engine.execute(f"DESCRIBE {tabela}")
                colunas = [row[0] for row in result]
                print(f"     Colunas: {', '.join(colunas)}")
            
            return True
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def testar_conexao():
    """
    Testa a conexao com MySQL
    """
    print("TESTANDO CONEXAO COM MYSQL...")
    
    try:
        # Credenciais
        connection = pymysql.connect(
            host='127.0.0.1',
            user='u419790683_l7nutri_alex',
            password='Duda@1401',
            database='u419790683_l7nutri_novo',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL conectado! Versao: {version[0]}")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"ERRO DE CONEXAO: {e}")
        return False

if __name__ == '__main__':
    print("=== SETUP MYSQL HOSTINGER ===")
    print("Credenciais:")
    print("  Usuario: u419790683_l7nutri_alex")
    print("  Host: 127.0.0.1")
    print("  Banco: u419790683_l7nutri_novo")
    print()
    
    if testar_conexao():
        print("\n" + "="*40)
        if criar_tabelas():
            print("\nSUCESSO! Banco configurado!")
        else:
            print("\nERRO ao criar tabelas!")
    else:
        print("\nERRO de conexao!")
