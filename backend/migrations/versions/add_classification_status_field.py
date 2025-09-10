"""Add product classification status field to categories

Revision ID: add_classification_status_field
Revises: c5b03fe8c42c
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_classification_status_field'
down_revision = 'c5b03fe8c42c'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new JSON field to print_product_categories table
    op.add_column('print_product_categories', 
                  sa.Column('product_classification_status', 
                           sa.JSON(), 
                           nullable=False, 
                           server_default='{"all_classified": true, "total_products": 0, "classified_products": 0, "unclassified_products": 0}'))


def downgrade():
    # Remove the product_classification_status column
    op.drop_column('print_product_categories', 'product_classification_status') 