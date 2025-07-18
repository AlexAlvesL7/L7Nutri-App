"""merge suplementos e instrucao_uso

Revision ID: merge_suplementos_instrucao_uso
Revises: add_suplementos, add_instrucao_uso_suplementos
Create Date: 2025-07-15 15:52:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_suplementos_instrucao_uso'
down_revision = ('add_suplementos', 'add_instrucao_uso_suplementos')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
