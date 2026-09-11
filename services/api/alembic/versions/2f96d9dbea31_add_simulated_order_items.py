"""add simulated order items and cancellation metadata

Revision ID: 2f96d9dbea31
Revises: cebf05c1e22e
Create Date: 2026-09-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f96d9dbea31"
down_revision: Union[str, Sequence[str], None] = "cebf05c1e22e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'cancelled'")
    op.add_column(
        "simulated_orders",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "simulated_orders",
        sa.Column("certificate_reference", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "simulated_orders",
        sa.Column("certificate_issued_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "simulated_orders",
        sa.Column("retirement_quantity", sa.Numeric(14, 3), nullable=True),
    )
    op.create_unique_constraint(
        op.f("uq_simulated_orders_certificate_reference"),
        "simulated_orders",
        ["certificate_reference"],
    )
    op.create_check_constraint(
        op.f("ck_simulated_orders_retirement_quantity_positive"),
        "simulated_orders",
        "retirement_quantity IS NULL OR retirement_quantity > 0",
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("credit_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("project_name_snapshot", sa.String(length=240), nullable=False),
        sa.Column("vintage", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_price_snapshot", sa.Numeric(14, 2), nullable=False),
        sa.Column("line_total_snapshot", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("char_length(currency) = 3", name=op.f("ck_order_items_currency_length")),
        sa.CheckConstraint("line_total_snapshot >= 0", name=op.f("ck_order_items_line_total_non_negative")),
        sa.CheckConstraint("quantity > 0", name=op.f("ck_order_items_quantity_positive")),
        sa.CheckConstraint("unit_price_snapshot >= 0", name=op.f("ck_order_items_unit_price_non_negative")),
        sa.ForeignKeyConstraint(
            ["credit_id"], ["carbon_credits.id"], name=op.f("fk_order_items_credit_id_carbon_credits"), ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["simulated_orders.id"], name=op.f("fk_order_items_order_id_simulated_orders"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name=op.f("fk_order_items_project_id_projects"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items")),
        sa.UniqueConstraint("order_id", "credit_id", name="uq_order_items_order_credit"),
    )
    op.create_index(op.f("ix_order_items_order_id"), "order_items", ["order_id"])
    op.create_index(op.f("ix_order_items_credit_id"), "order_items", ["credit_id"])
    op.create_index(op.f("ix_order_items_project_id"), "order_items", ["project_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_order_items_project_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_credit_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_table("order_items")
    op.drop_constraint(
        op.f("ck_simulated_orders_retirement_quantity_positive"),
        "simulated_orders",
        type_="check",
    )
    op.drop_constraint(
        op.f("uq_simulated_orders_certificate_reference"),
        "simulated_orders",
        type_="unique",
    )
    op.drop_column("simulated_orders", "retirement_quantity")
    op.drop_column("simulated_orders", "certificate_issued_at")
    op.drop_column("simulated_orders", "certificate_reference")
    op.drop_column("simulated_orders", "cancelled_at")
