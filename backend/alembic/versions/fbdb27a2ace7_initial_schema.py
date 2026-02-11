"""initial_schema

Revision ID: fbdb27a2ace7
Revises: 
Create Date: 2026-02-08 04:53:27.590261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import pgvector

# revision identifiers, used by Alembic.
revision: str = 'fbdb27a2ace7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('project_chunks',
      sa.Column('id', sa.Integer(), nullable=False),
      sa.Column('project_id', sa.String(), nullable=True),
      sa.Column('content', sa.Text(), nullable=True),
      sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
      sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
      sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_project_chunks_search_vector', 'project_chunks', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_project_chunks_project_id'), 'project_chunks', ['project_id'], unique=False)

    op.execute("""
      CREATE TEXT SEARCH DICTIONARY ukrainian_hunspell (
        TEMPLATE = ispell,
        DictFile = uk_ua,
        AffFile = uk_ua,
        StopWords = ukrainian
      );
    """)

    op.execute("""
      DO $$ 
      BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'ukrainian') THEN
          CREATE TEXT SEARCH CONFIGURATION public.ukrainian (COPY = pg_catalog.simple);
        END IF;
      END $$;
    """)

    op.execute("""
      ALTER TEXT SEARCH CONFIGURATION public.ukrainian 
      ALTER MAPPING FOR word, hword, hword_part 
      WITH ukrainian_hunspell, simple;
    """)

    op.execute("""
      CREATE OR REPLACE FUNCTION chunks_search_vector_update() RETURNS trigger AS $$
      BEGIN
        new.search_vector := to_tsvector('ukrainian', coalesce(new.content, ''));
        RETURN new;
      END
      $$ LANGUAGE plpgsql;
    """)

    op.execute("""
      CREATE TRIGGER trg_search_vector_update
      BEFORE INSERT OR UPDATE ON project_chunks
      FOR EACH ROW EXECUTE FUNCTION chunks_search_vector_update();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_project_chunks_project_id'), table_name='project_chunks')
    op.drop_index('idx_project_chunks_search_vector', table_name='project_chunks', postgresql_using='gin')
    op.drop_table('project_chunks')
