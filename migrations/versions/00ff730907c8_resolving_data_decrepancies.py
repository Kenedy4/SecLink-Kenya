"""Resolving Data decrepancies

Revision ID: 00ff730907c8
Revises: 
Create Date: 2024-10-24 17:11:23.225564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00ff730907c8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_parents')),
    sa.UniqueConstraint('email', name=op.f('uq_parents_email')),
    sa.UniqueConstraint('username', name=op.f('uq_parents_username'))
    )
    op.create_table('teachers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_teachers')),
    sa.UniqueConstraint('email', name=op.f('uq_teachers_email')),
    sa.UniqueConstraint('username', name=op.f('uq_teachers_username'))
    )
    op.create_table('classes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('class_name', sa.String(length=50), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_classes_teacher_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_classes'))
    )
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['parents.id'], name=op.f('fk_notifications_parent_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications'))
    )
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dob', sa.Date(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=False),
    sa.Column('overall_grade', sa.String(length=2), nullable=True),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name=op.f('fk_students_class_id')),
    sa.ForeignKeyConstraint(['parent_id'], ['parents.id'], name=op.f('fk_students_parent_id')),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_students_teacher_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_students'))
    )
    op.create_table('subjects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject_name', sa.String(length=100), nullable=False),
    sa.Column('subject_code', sa.String(length=10), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name=op.f('fk_subjects_class_id')),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_subjects_teacher_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_subjects'))
    )
    op.create_table('grades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('grade', sa.String(length=2), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_grades_student_id')),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name=op.f('fk_grades_subject_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_grades'))
    )
    op.create_table('learning_material',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('file_path', sa.String(length=200), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_learning_material_student_id')),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_learning_material_teacher_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_learning_material'))
    )
    op.create_table('password_reset_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=100), nullable=False),
    sa.Column('expiry_date', sa.DateTime(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['parents.id'], name=op.f('fk_password_reset_tokens_parent_id')),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_password_reset_tokens_student_id')),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_password_reset_tokens_teacher_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_password_reset_tokens')),
    sa.UniqueConstraint('token', name=op.f('uq_password_reset_tokens_token'))
    )
    op.create_table('student_subject',
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('student_name', sa.String(length=100), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name=op.f('fk_student_subject_class_id')),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_student_subject_student_id')),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name=op.f('fk_student_subject_subject_id'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student_subject')
    op.drop_table('password_reset_tokens')
    op.drop_table('learning_material')
    op.drop_table('grades')
    op.drop_table('subjects')
    op.drop_table('students')
    op.drop_table('notifications')
    op.drop_table('classes')
    op.drop_table('teachers')
    op.drop_table('parents')
    # ### end Alembic commands ###