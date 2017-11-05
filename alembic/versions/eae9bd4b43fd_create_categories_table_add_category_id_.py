"""create categories table; add category_id to events table

Revision ID: eae9bd4b43fd
Revises: 
Create Date: 2017-10-25 09:54:40.730642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eae9bd4b43fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'categories',
        sa.Column('category_id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False)
    )

    op.add_column('events', sa.Column(
        sa.BigInteger(),
        sa.ForeignKey("categories.category_id"),
        nullable=False
    ))


def downgrade():
    op.drop_table('categories')
    op.drop_column('events', 'category_id')
