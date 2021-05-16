"""empty message

Revision ID: a74a57c52078
Revises: 3b6f0bbea91f
Create Date: 2021-05-15 23:56:57.584511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a74a57c52078'
down_revision = '3b6f0bbea91f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue','website_link', new_column_name = 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue','website', new_column_name = 'website_link')
    # ### end Alembic commands ###
