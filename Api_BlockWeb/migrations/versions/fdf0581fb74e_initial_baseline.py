"""initial baseline

Revision ID: fdf0581fb74e
Revises: 
Create Date: 2026-08-21 15:33:20.031294

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'fdf0581fb74e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ========================================================
    # WEB POLICY
    # ========================================================

    op.create_table(
        "web_policy",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "name",
            sa.String(
                length=100
            ),
            nullable=False,
        ),

        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "working_start",
            sa.Time(),
            nullable=False,
        ),

        sa.Column(
            "working_end",
            sa.Time(),
            nullable=False,
        ),

        sa.Column(
            "working_days",
            postgresql.ARRAY(
                sa.Integer()
            ),
            nullable=False,
        ),

    )


    # ========================================================
    # POLICY RULE
    # ========================================================

    op.create_table(

        "web_policy_rule",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "policy_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "rule_type",
            sa.String(
                length=20
            ),
            nullable=False,
        ),

        sa.Column(
            "host",
            sa.String(
                length=255
            ),
            nullable=False,
        ),

        sa.Column(
            "path",
            sa.String(
                length=500
            ),
            nullable=False,
        ),

        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(

            ["policy_id"],

            ["web_policy.id"],

            ondelete="CASCADE",

        ),

    )


    op.create_index(

        "ix_web_policy_rule_policy_id",

        "web_policy_rule",

        ["policy_id"],

        unique=False,

    )


    # ========================================================
    # DEPARTMENT
    # ========================================================

    op.create_table(

        "department",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "code",
            sa.String(
                length=50
            ),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(
                length=150
            ),
            nullable=False,
        ),

        sa.Column(
            "policy_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(

            ["policy_id"],

            ["web_policy.id"],

            ondelete="SET NULL",

        ),

        sa.UniqueConstraint(
            "code"
        ),

    )


    op.create_index(

        "ix_department_code",

        "department",

        ["code"],

        unique=True,

    )


    op.create_index(

        "ix_department_policy_id",

        "department",

        ["policy_id"],

        unique=False,

    )


    # ========================================================
    # EMPLOYEE
    # ========================================================

    op.create_table(

        "employee",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "employee_code",
            sa.String(
                length=50
            ),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(
                length=150
            ),
            nullable=False,
        ),

        sa.Column(
            "department_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(

            ["department_id"],

            ["department.id"],

            ondelete="SET NULL",

        ),

        sa.UniqueConstraint(
            "employee_code"
        ),

    )


    op.create_index(

        "ix_employee_employee_code",

        "employee",

        ["employee_code"],

        unique=True,

    )


    op.create_index(

        "ix_employee_department_id",

        "employee",

        ["department_id"],

        unique=False,

    )


    # ========================================================
    # DEVICE
    # ========================================================

    op.create_table(

        "device",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "device_uid",
            sa.String(
                length=100
            ),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(
                length=150
            ),
            nullable=False,
        ),

        sa.Column(
            "employee_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "api_key_hash",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.Column(
            "last_seen_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(

            ["employee_id"],

            ["employee.id"],

            ondelete="SET NULL",

        ),

        sa.UniqueConstraint(
            "device_uid"
        ),

    )


    op.create_index(

        "ix_device_device_uid",

        "device",

        ["device_uid"],

        unique=True,

    )


    op.create_index(

        "ix_device_employee_id",

        "device",

        ["employee_id"],

        unique=False,

    )


    # ========================================================
    # ACCESS LOG
    # ========================================================

    op.create_table(

        "access_log",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "client_log_id",
            sa.String(
                length=100
            ),
            nullable=False,
        ),

        sa.Column(
            "device_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "decision",
            sa.String(
                length=20
            ),
            nullable=False,
        ),

        sa.Column(
            "reason",
            sa.String(
                length=100
            ),
            nullable=False,
        ),

        sa.Column(
            "url",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "hostname",
            sa.String(
                length=255
            ),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "event_time",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.Column(
            "received_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(

            ["device_id"],

            ["device.id"],

            ondelete="RESTRICT",

        ),

        sa.UniqueConstraint(
            "client_log_id"
        ),

    )


    op.create_index(

        "ix_access_log_client_log_id",

        "access_log",

        ["client_log_id"],

        unique=True,

    )


    op.create_index(

        "ix_access_log_device_id",

        "access_log",

        ["device_id"],

        unique=False,

    )


    op.create_index(

        "ix_access_log_decision",

        "access_log",

        ["decision"],

        unique=False,

    )


    op.create_index(

        "ix_access_log_hostname",

        "access_log",

        ["hostname"],

        unique=False,

    )


    # ========================================================
    # ENROLLMENT TOKEN
    # ========================================================

    op.create_table(

        "enrollment_token",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "token_hash",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.String(
                length=200
            ),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.Column(
            "used_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.Column(
            "used_by_device_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(

            ["used_by_device_id"],

            ["device.id"],

            ondelete="SET NULL",

        ),

        sa.UniqueConstraint(
            "token_hash"
        ),

    )


    op.create_index(

        "ix_enrollment_token_token_hash",

        "enrollment_token",

        ["token_hash"],

        unique=True,

    )


def downgrade() -> None:

    op.drop_index(
        "ix_enrollment_token_token_hash",
        table_name="enrollment_token",
    )

    op.drop_table(
        "enrollment_token"
    )


    op.drop_index(
        "ix_access_log_hostname",
        table_name="access_log",
    )

    op.drop_index(
        "ix_access_log_decision",
        table_name="access_log",
    )

    op.drop_index(
        "ix_access_log_device_id",
        table_name="access_log",
    )

    op.drop_index(
        "ix_access_log_client_log_id",
        table_name="access_log",
    )

    op.drop_table(
        "access_log"
    )


    op.drop_index(
        "ix_device_employee_id",
        table_name="device",
    )

    op.drop_index(
        "ix_device_device_uid",
        table_name="device",
    )

    op.drop_table(
        "device"
    )


    op.drop_index(
        "ix_employee_department_id",
        table_name="employee",
    )

    op.drop_index(
        "ix_employee_employee_code",
        table_name="employee",
    )

    op.drop_table(
        "employee"
    )


    op.drop_index(
        "ix_department_policy_id",
        table_name="department",
    )

    op.drop_index(
        "ix_department_code",
        table_name="department",
    )

    op.drop_table(
        "department"
    )


    op.drop_index(
        "ix_web_policy_rule_policy_id",
        table_name="web_policy_rule",
    )

    op.drop_table(
        "web_policy_rule"
    )


    op.drop_table(
        "web_policy"
    )
