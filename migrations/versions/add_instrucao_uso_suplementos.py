"""add coluna instrucao_uso em suplementos

Revision ID: add_instrucao_uso_suplementos
Revises: add_perfis_nutricionais
Create Date: 2025-07-15 15:45:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_instrucao_uso_suplementos'
down_revision = 'add_perfis_nutricionais'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('suplementos', sa.Column('instrucao_uso', sa.String(255)))

def downgrade():
    op.drop_column('suplementos', 'instrucao_uso')
