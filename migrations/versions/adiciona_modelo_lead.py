"""Adiciona modelo Lead para sistema de captura

Revision ID: lead_capture_2025
Revises: 6280d7d2a288
Create Date: 2025-07-20 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'lead_capture_2025'
down_revision = '6280d7d2a288'
branch_labels = None
depends_on = None


def upgrade():
    # ### Criar tabela Lead ###
    op.create_table('lead',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=True),
    sa.Column('telefone', sa.String(length=20), nullable=True),
    sa.Column('objetivo', sa.String(length=200), nullable=True),
    sa.Column('fonte', sa.String(length=50), nullable=True),
    sa.Column('utm_source', sa.String(length=100), nullable=True),
    sa.Column('utm_medium', sa.String(length=100), nullable=True),
    sa.Column('utm_campaign', sa.String(length=100), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('convertido', sa.Boolean(), nullable=True, default=False),
    sa.Column('data_conversao', sa.DateTime(), nullable=True),
    sa.Column('contador_interacoes', sa.Integer(), nullable=True, default=1),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_email'), 'lead', ['email'], unique=True)
    op.create_index(op.f('ix_lead_created_at'), 'lead', ['created_at'], unique=False)
    op.create_index(op.f('ix_lead_fonte'), 'lead', ['fonte'], unique=False)


def downgrade():
    # ### Remover tabela Lead ###
    op.drop_index(op.f('ix_lead_fonte'), table_name='lead')
    op.drop_index(op.f('ix_lead_created_at'), table_name='lead')
    op.drop_index(op.f('ix_lead_email'), table_name='lead')
    op.drop_table('lead')
