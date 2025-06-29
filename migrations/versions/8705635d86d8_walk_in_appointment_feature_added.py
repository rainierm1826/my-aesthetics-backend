"""walk in appointment feature added

Revision ID: 8705635d86d8
Revises: 4958af7d1c06
Create Date: 2025-06-26 13:16:34.056303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8705635d86d8'
down_revision = '4958af7d1c06'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('aesthetician', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sex', sa.Enum('male', 'female', 'others', name='sex_enum'), nullable=True, create_type=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('aesthetician', schema=None) as batch_op:
        batch_op.drop_column('sex')

    # ### end Alembic commands ###
