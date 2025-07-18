#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar conectividade com diferentes configuracoes MySQL
"""

import pymysql
import os

def testar_hostinger_remoto():
    """
    Testa conexao com servidor MySQL remoto da Hostinger
    """
    print("TESTANDO CONEXAO REMOTA HOSTINGER...")
    
    # Possibilidades de host da Hostinger
    hosts = [
        'localhost',  # Quando estiver no servidor
        '127.0.0.1',  # Local
        'sql01.hostinger.com',  # Servidor remoto possivel
        'mysql.hostinger.com',  # Servidor remoto possivel
    ]
    
    for host in hosts:
        try:
            print(f"Tentando conectar em: {host}")
            
            connection = pymysql.connect(
                host=host,
                user='u419790683_l7nutri_alex',
                password='Duda@1401',
                database='u419790683_l7nutri_novo',
                charset='utf8mb4',
                connect_timeout=5
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"SUCESSO! Conectado em {host}")
                print(f"Versao MySQL: {version[0]}")
                
                # Listar tabelas existentes
                cursor.execute("SHOW TABLES")
                tabelas = cursor.fetchall()
                print(f"Tabelas existentes: {len(tabelas)}")
                for tabela in tabelas:
                    print(f"  - {tabela[0]}")
                
            connection.close()
            return host
            
        except Exception as e:
            print(f"ERRO em {host}: {e}")
            
    return None

def criar_tabelas_remotas(host):
    """
    Cria tabelas via SQL direto no servidor remoto
    """
    print(f"CRIANDO TABELAS NO SERVIDOR: {host}")
    
    try:
        connection = pymysql.connect(
            host=host,
            user='u419790683_l7nutri_alex',
            password='Duda@1401',
            database='u419790683_l7nutri_novo',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Criar tabela usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome_usuario VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    senha_hash VARCHAR(255) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Criar tabela alimentos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alimentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    calorias DECIMAL(10,2) NOT NULL,
                    proteinas DECIMAL(10,2) NOT NULL,
                    carboidratos DECIMAL(10,2) NOT NULL,
                    gorduras DECIMAL(10,2) NOT NULL
                )
            """)
            
            # Criar tabela diarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    data_entrada DATE NOT NULL,
                    alimento_id INT NOT NULL,
                    quantidade DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
                )
            """)
            
        connection.commit()
        
        # Verificar tabelas criadas
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()
            print(f"TABELAS CRIADAS: {len(tabelas)}")
            for tabela in tabelas:
                print(f"  - {tabela[0]}")
                
        connection.close()
        return True
        
    except Exception as e:
        print(f"ERRO ao criar tabelas: {e}")
        return False

if __name__ == '__main__':
    print("=== TESTE CONECTIVIDADE MYSQL HOSTINGER ===")
    print()
    
    host_funcional = testar_hostinger_remoto()
    
    if host_funcional:
        print(f"\nCONEXAO ESTABELECIDA COM: {host_funcional}")
        
        if criar_tabelas_remotas(host_funcional):
            print("\nTABELAS CRIADAS COM SUCESSO!")
        else:
            print("\nERRO ao criar tabelas!")
    else:
        print("\nNENHUM SERVIDOR MYSQL ACESSIVEL!")
        print("Possibilidades:")
        print("1. MySQL ainda nao configurado na Hostinger")
        print("2. Host/IP incorreto")
        print("3. Firewall bloqueando conexoes remotas")
        print("4. Credenciais incorretas")
