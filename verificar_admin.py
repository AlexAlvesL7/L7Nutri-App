import sqlite3
from flask_bcrypt import Bcrypt

# Conectar ao banco
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

print("🔍 VERIFICANDO USUÁRIO ADMINISTRADOR...")

# Verificar se existe a tabela usuario
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
tabela_existe = cursor.fetchone()

if tabela_existe:
    print('✅ Tabela usuario existe')
    
    # Verificar se existe o usuário admin
    cursor.execute('SELECT id, nome, email FROM usuario WHERE email = ? OR email = ?', 
                   ('admin@l7nutri.com', 'admin'))
    admin = cursor.fetchone()
    
    if admin:
        print(f'✅ Usuário admin encontrado: ID={admin[0]}, Nome={admin[1]}, Email={admin[2]}')
        print('📝 Credenciais de login:')
        print('   👤 Usuário: admin@l7nutri.com OU admin')
        print('   🔑 Senha: admin123')
    else:
        print('❌ Usuário admin NÃO encontrado. Criando...')
        
        # Criar usuário admin
        bcrypt = Bcrypt()
        senha_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        
        cursor.execute('''
            INSERT INTO usuario (nome, email, senha, idade, peso, altura, sexo, nivel_atividade, objetivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Administrador', 'admin@l7nutri.com', senha_hash, 30, 70.0, 175.0, 'M', 'moderado', 'manter'))
        
        conn.commit()
        print('✅ Usuário admin criado com sucesso!')
        print('📧 Email: admin@l7nutri.com')
        print('🔑 Senha: admin123')
        
        # Criar também com email simples "admin"
        cursor.execute('''
            INSERT INTO usuario (nome, email, senha, idade, peso, altura, sexo, nivel_atividade, objetivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Admin Simples', 'admin', senha_hash, 30, 70.0, 175.0, 'M', 'moderado', 'manter'))
        
        conn.commit()
        print('✅ Usuário admin simples também criado!')
        print('👤 Login alternativo: admin')
        print('🔑 Senha: admin123')
else:
    print('❌ Tabela usuario não existe. Execute python criar_banco.py primeiro!')

# Listar todos os usuários
print('\n📋 TODOS OS USUÁRIOS NO BANCO:')
cursor.execute('SELECT id, nome, email FROM usuario')
usuarios = cursor.fetchall()

if usuarios:
    for user in usuarios:
        print(f'   🔹 ID: {user[0]} | Nome: {user[1]} | Email: {user[2]}')
else:
    print('   📭 Nenhum usuário encontrado')

conn.close()
print('\n🎯 AGORA VOCÊ PODE FAZER LOGIN COM:')
print('   👤 Usuário: admin')
print('   🔑 Senha: admin123')
print('   OU')
print('   👤 Email: admin@l7nutri.com')
print('   🔑 Senha: admin123')
