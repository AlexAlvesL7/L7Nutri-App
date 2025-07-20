"""Fix: Reorganiza estrutura do banco para produção

Revision ID: emergency_fix
Revises: 0b2cbf484f40
Create Date: 2025-07-19 11:22:51.467284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'emergency_fix'
down_revision = '0b2cbf484f40'
branch_labels = None
depends_on = None


def upgrade():
    # Cria tabela suplementos se não existir
    op.create_table('suplementos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('objetivo', sa.String(30)),
        sa.Column('link_loja', sa.String(255)),
        sa.Column('imagem_url', sa.String(255)),
        sa.Column('instrucao_uso', sa.String(255))  # Já inclui a coluna
    )
    
    # Cria tabela perfis_nutricionais se não existir
    op.create_table('perfis_nutricionais',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('peso', sa.Float()),
        sa.Column('altura', sa.Integer()),
        sa.Column('idade', sa.Integer()),
        sa.Column('genero', sa.String(20)),
        sa.Column('nivel_atividade', sa.String(30)),
        sa.Column('objetivo', sa.String(30)),
        sa.Column('aceita_suplementos', sa.Boolean()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('usuario.id')),
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp())
    )


def downgrade():
    op.drop_table('perfis_nutricionais')
    op.drop_table('suplementos')
