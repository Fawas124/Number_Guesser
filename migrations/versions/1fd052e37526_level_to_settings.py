"""level to settings

Revision ID: 1fd052e37526
Revises: 288c3d692085
Create Date: 2025-05-06 21:56:17.892552

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1fd052e37526'
down_revision = '288c3d692085'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_sessions', schema=None) as batch_op:
        batch_op.drop_column('secret_word')

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('level', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('range_low', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('range_high', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('max_attempts', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))
        batch_op.create_unique_constraint(None, ['level'])
        batch_op.drop_column('max_attempts_hard')
        batch_op.drop_column('score_multiplier_hard')
        batch_op.drop_column('max_attempts_easy')
        batch_op.drop_column('score_multiplier_medium')
        batch_op.drop_column('max_attempts_medium')
        batch_op.drop_column('maintenance_mode')
        batch_op.drop_column('app_name')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('score_multiplier_easy')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score_multiplier_easy', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('app_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('maintenance_mode', sa.BOOLEAN(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('max_attempts_medium', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('score_multiplier_medium', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('max_attempts_easy', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('score_multiplier_hard', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('max_attempts_hard', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('is_active')
        batch_op.drop_column('max_attempts')
        batch_op.drop_column('range_high')
        batch_op.drop_column('range_low')
        batch_op.drop_column('level')

    with op.batch_alter_table('game_sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('secret_word', sa.VARCHAR(length=100), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
