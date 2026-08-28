"""initialize database

Revision ID: 5316ace179ad
Revises:
Create Date: 2026-08-28 22:46:16.187760

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "5316ace179ad"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
