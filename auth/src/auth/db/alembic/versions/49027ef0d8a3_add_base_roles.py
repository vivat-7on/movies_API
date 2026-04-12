"""Add base roles

Revision ID: 49027ef0d8a3
Revises: 4a1781241964
Create Date: 2026-04-12 18:28:22.850974

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49027ef0d8a3"
down_revision: Union[str, Sequence[str], None] = "4a1781241964"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

base_roles = ["user", "admin", "superuser"]


def upgrade() -> None:
    """Upgrade schema."""
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
    )
    roles = [{"id": uuid.uuid4(), "name": role} for role in base_roles]

    op.bulk_insert(roles_table, roles)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text(
            "DELETE FROM roles WHERE name IN ('user', 'admin', 'superuser')",
        ),
    )
