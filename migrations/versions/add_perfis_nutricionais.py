"""cria tabela perfis_nutricionais

Revision ID: add_perfis_nutricionais
Revises: 7e96ed3de706
Create Date: 2025-07-15 15:30:00
"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'add_perfis_nutricionais'
down_revision = '7e96ed3de706'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'perfis_nutricionais',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('peso', sa.Float),
        sa.Column('altura', sa.Integer),
        sa.Column('idade', sa.Integer),
        sa.Column('genero', sa.String(20)),
        sa.Column('nivel_atividade', sa.String(30)),
        sa.Column('objetivo', sa.String(30)),
        sa.Column('aceita_suplementos', sa.Boolean),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('usuario.id')),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.utcnow)
    )

def downgrade():
    op.drop_table('perfis_nutricionais')
