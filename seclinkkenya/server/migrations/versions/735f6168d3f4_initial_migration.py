"""Initial migration

Revision ID: 735f6168d3f4
Revises: 
Create Date: 2024-10-16 04:12:49.060971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '735f6168d3f4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('_password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('password_reset_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=100), nullable=False),
    sa.Column('expiry_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teacher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('_password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('class',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('class_name', sa.String(length=50), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parent_notification',
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('notification_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['parent.id'], )
    )
    op.create_table('student',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('dob', sa.Date(), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('_password_hash', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject_name', sa.String(length=100), nullable=False),
    sa.Column('subject_code', sa.String(length=10), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('learning_material',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('file_path', sa.String(length=200), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student_notification',
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('notification_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], )
    )
    op.create_table('student_subject',
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student_subject')
    op.drop_table('student_notification')
    op.drop_table('learning_material')
    op.drop_table('subject')
    op.drop_table('student')
    op.drop_table('parent_notification')
    op.drop_table('class')
    op.drop_table('teacher')
    op.drop_table('password_reset_token')
    op.drop_table('parent')
    op.drop_table('notification')
    # ### end Alembic commands ###