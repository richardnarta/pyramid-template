"""create user table

Revision ID: e3cf8bcbb80d
Revises: f47d6f9a147d
Create Date: 2025-06-07 11:49:31.123368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3cf8bcbb80d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tblUser',
        sa.Column(
            'user_id',
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            'user_phone',
            sa.String(length=17),
            nullable=True
        ),
        sa.Column(
            'user_username',
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            'user_name',
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            'user_email',
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            'user_password',
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            'user_is_verified',
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            'user_is_login',
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            'user_role',
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            'user_created_at',
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            'user_updated_at',
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            'user_approved_at',
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            'user_reject_message',
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            'user_status',
            sa.Enum(
                'deleted',
                'active',
                'inactive',
                name='userstatusenum'
            ),
            nullable=False
        ),
        sa.Column(
            'user_created_by',
            sa.String(length=255),
            nullable=True
        ),
        sa.Column(
            'user_approved_by',
            sa.String(length=255),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ['user_created_by'],
            ['tblUser.user_id'],
            name=op.f('fk_tblUser_user_created_by_tblUser'),
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_approved_by'],
            ['tblUser.user_id'],
            name=op.f('fk_tblUser_user_approved_by_tblUser'),
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint(
            'user_id',
            name=op.f('pk_tblUser')
        ),
        sa.UniqueConstraint(
            'user_phone',
            name=op.f('uq_tblUser_user_phone')
        ),
        sa.UniqueConstraint(
            'user_username',
            name=op.f('uq_tblUser_user_username')
        )
    )

    op.create_index(
        op.f('ix_tblUser_user_role'),
        'tblUser',
        ['user_role'],
        unique=False
    )


def downgrade():
    op.drop_table('tblUser')
