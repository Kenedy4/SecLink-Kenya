"""Add parent-student relationship

Revision ID: 5628d724bf21
Revises: 735f6168d3f4
Create Date: 2024-10-16 04:28:58.637747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5628d724bf21'
down_revision = '735f6168d3f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_student_parent', 'parent', ['parent_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('parent_id')

    # ### end Alembic commands ###