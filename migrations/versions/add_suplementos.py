"""cria tabela suplementos

Revision ID: add_suplementos
Revises: add_perfis_nutricionais
Create Date: 2025-07-15 15:50:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_suplementos'
down_revision = 'add_perfis_nutricionais'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'suplementos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('objetivo', sa.String(30)),
        sa.Column('link_loja', sa.String(255)),
        sa.Column('imagem_url', sa.String(255)),
        sa.Column('instrucao_uso', sa.String(255))
    )

def downgrade():
    op.drop_table('suplementos')
