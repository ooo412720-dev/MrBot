"""full migration

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-02 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group_settings",
        sa.Column("group_id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("welcome_text", sa.Text(), nullable=True),
        sa.Column("rules_text", sa.Text(), nullable=True),
        sa.Column("captcha_enabled", sa.Boolean(), server_default="true"),
        sa.Column("antilink_enabled", sa.Boolean(), server_default="true"),
        sa.Column("welcome_enabled", sa.Boolean(), server_default="true"),
        sa.Column("antispam_enabled", sa.Boolean(), server_default="true"),
        sa.Column("lock_media", sa.Boolean(), server_default="false"),
        sa.Column("lock_stickers", sa.Boolean(), server_default="false"),
        sa.Column("lock_forward", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "filtered_words",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("word", sa.String(128), nullable=False),
        sa.Column("reply", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "warnings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "mutes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "user_points",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("points", sa.Integer(), server_default="0"),
        sa.Column("reputation", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "captchas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("answer", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.add_column("users", sa.Column("role", sa.String(30), server_default="member"))


def downgrade() -> None:
    op.drop_table("captchas")
    op.drop_table("logs")
    op.drop_table("user_points")
    op.drop_table("mutes")
    op.drop_table("warnings")
    op.drop_table("filtered_words")
    op.drop_table("notes")
    op.drop_table("group_settings")
    op.drop_column("users", "role")
