"""new fields in user model

Revision ID: 5c0bd85e074b
Revises: 15353e22a6bc
Create Date: 2023-09-06 10:53:37.185115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c0bd85e074b'
down_revision = '15353e22a6bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_me', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_seen')
        batch_op.drop_column('about_me')

    # ### end Alembic commands ###
