"""add_soft_delete_to_preventivi

Revision ID: 5546c88458bf
Revises: eba5926e0b26
Create Date: 2025-05-24 16:58:25.259440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5546c88458bf'
down_revision: Union[str, None] = 'eba5926e0b26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('preventivi', sa.Column('stato_record', sa.String(length=50), nullable=False, server_default='attivo', index=True))
    op.add_column('preventivi', sa.Column('cestinato_il', sa.DateTime(), nullable=True, index=True))
    # Se si decide di NON usare server_default per 'stato_record' per non bloccare tabelle grandi,
    # si dovrebbe fare un update separato dopo add_column con nullable=True, poi alter_column a nullable=False.
    # op.execute("UPDATE preventivi SET stato_record = 'attivo' WHERE stato_record IS NULL")
    # op.alter_column('preventivi', 'stato_record', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('preventivi', 'cestinato_il')
    op.drop_column('preventivi', 'stato_record')
