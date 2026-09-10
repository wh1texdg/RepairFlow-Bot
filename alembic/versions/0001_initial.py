"""initial RepairFlow schema"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


request_status = sa.Enum(
    "NEW",
    "IN_PROGRESS",
    "CONTACTED",
    "CALCULATING",
    "APPROVED",
    "REJECTED",
    "COMPLETED",
    name="request_status",
)

user_role = sa.Enum(
    "CLIENT",
    "MANAGER",
    "ADMIN",
    name="user_role",
)


def upgrade() -> None:
    # bind = op.get_bind()
    # request_status.create(bind, checkfirst=True)
    # user_role.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255)),
        sa.Column("name", sa.String(length=255)),
        sa.Column("phone", sa.String(length=32)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=False)

    op.create_table(
        "managers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="MANAGER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_managers_telegram_id", "managers", ["telegram_id"], unique=False)

    op.create_table(
        "requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("object_type", sa.String(length=100), nullable=False),
        sa.Column("repair_type", sa.String(length=100), nullable=False),
        sa.Column("area", sa.Numeric(10, 2), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("budget", sa.Numeric(14, 2), nullable=False),
        sa.Column("desired_start_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", request_status, nullable=False, server_default="NEW"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint("area > 0", name="ck_requests_area_positive"),
        sa.CheckConstraint("area <= 10000", name="ck_requests_area_reasonable"),
        sa.CheckConstraint("budget >= 0", name="ck_requests_budget_non_negative"),
    )
    op.create_index("ix_requests_status_created_at", "requests", ["status", "created_at"])
    op.create_index("ix_requests_user_id_created_at", "requests", ["user_id", "created_at"])

    op.create_table(
        "request_status_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("old_status", request_status),
        sa.Column("new_status", request_status, nullable=False),
        sa.Column("changed_by", sa.Integer()),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["managers.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_request_status_history_request_id", "request_status_history", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_request_status_history_request_id", table_name="request_status_history")
    op.drop_table("request_status_history")
    op.drop_index("ix_requests_user_id_created_at", table_name="requests")
    op.drop_index("ix_requests_status_created_at", table_name="requests")
    op.drop_table("requests")
    op.drop_index("ix_managers_telegram_id", table_name="managers")
    op.drop_table("managers")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    user_role.drop(op.get_bind(), checkfirst=True)
    request_status.drop(op.get_bind(), checkfirst=True)
