"""Change IDs format from str to UUID

Revision ID: 9134a3b1217d
Revises: 7939044b4918
Create Date: 2026-03-16 15:55:17.315085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9134a3b1217d'
down_revision: Union[str, Sequence[str], None] = '7939044b4918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('todos_user_id_fkey', 'todos', type_='foreignkey')

    op.alter_column('users', 'id',
               existing_type=sa.VARCHAR(),
               type_=sa.Uuid(),
               existing_nullable=False,
               postgresql_using='id::uuid')

    op.alter_column('todos', 'id',
               existing_type=sa.VARCHAR(),
               type_=sa.Uuid(),
               existing_nullable=False,
               postgresql_using='id::uuid')

    op.alter_column('todos', 'user_id',
               existing_type=sa.VARCHAR(),
               type_=sa.Uuid(),
               existing_nullable=False,
               postgresql_using='user_id::uuid')

    op.create_foreign_key('todos_user_id_fkey', 'todos', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('todos_user_id_fkey', 'todos', type_='foreignkey')

    op.alter_column('users', 'id',
               existing_type=sa.Uuid(),
               type_=sa.VARCHAR(),
               existing_nullable=False)

    op.alter_column('todos', 'id',
               existing_type=sa.Uuid(),
               type_=sa.VARCHAR(),
               existing_nullable=False)

    op.alter_column('todos', 'user_id',
               existing_type=sa.Uuid(),
               type_=sa.VARCHAR(),
               existing_nullable=False)

    op.create_foreign_key('todos_user_id_fkey', 'todos', 'users', ['user_id'], ['id'])
