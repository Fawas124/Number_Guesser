"""add created_at to word

Revision ID: 7d6aef9fb4e2
Revises: a1fd75f8ad69
Create Date: 2025-05-05 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '7d6aef9fb4e2'
down_revision = 'a1fd75f8ad69'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('word', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.execute("UPDATE word SET is_active = true")  # Set default
    op.alter_column('word', 'is_active', nullable=False)

def downgrade():
    op.drop_column('word', 'is_active')