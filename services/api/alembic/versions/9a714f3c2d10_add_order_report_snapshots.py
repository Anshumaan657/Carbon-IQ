"""add immutable order report snapshots

Revision ID: 9a714f3c2d10
Revises: 2f96d9dbea31
Create Date: 2026-09-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "9a714f3c2d10"
down_revision: Union[str, Sequence[str], None] = "2f96d9dbea31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("order_items", sa.Column("registry_snapshot", sa.String(160)))
    op.add_column("order_items", sa.Column("methodology_snapshot", sa.String(255)))
    op.add_column("order_items", sa.Column("source_url_snapshot", sa.Text()))
    op.add_column("order_items", sa.Column("data_as_of_snapshot", sa.Date()))
    op.add_column("order_items", sa.Column("carboniq_score_snapshot", sa.Numeric(5, 2)))
    op.add_column("order_items", sa.Column("quality_score_snapshot", sa.Numeric(5, 2)))
    op.add_column("order_items", sa.Column("risk_score_snapshot", sa.Numeric(5, 2)))
    op.add_column(
        "order_items",
        sa.Column("score_methodology_version_snapshot", sa.String(40)),
    )
    op.add_column("order_items", sa.Column("risk_signals_snapshot", postgresql.JSONB()))


def downgrade() -> None:
    op.drop_column("order_items", "risk_signals_snapshot")
    op.drop_column("order_items", "score_methodology_version_snapshot")
    op.drop_column("order_items", "risk_score_snapshot")
    op.drop_column("order_items", "quality_score_snapshot")
    op.drop_column("order_items", "carboniq_score_snapshot")
    op.drop_column("order_items", "data_as_of_snapshot")
    op.drop_column("order_items", "source_url_snapshot")
    op.drop_column("order_items", "methodology_snapshot")
    op.drop_column("order_items", "registry_snapshot")
