"""Initial database schema for prospects, batch jobs, score results, rating flags, and reports.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-21 10:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Batch Jobs Table
    op.create_table(
        'batch_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column(
            'source',
            sa.Enum('manual_bulk', 'hubspot', 'excel_upload', name='batch_source_enum'),
            nullable=False,
            server_default='manual_bulk',
        ),
        sa.Column(
            'status',
            sa.Enum('queued', 'running', 'completed', 'partially_failed', 'failed', 'cancelled', name='batch_status_enum'),
            nullable=False,
            server_default='queued',
        ),
        sa.Column('total_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('flagged_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_batch_jobs_status'), 'batch_jobs', ['status'], unique=False)

    # 2. Prospects Table
    op.create_table(
        'prospects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('website_url', sa.String(length=512), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_title', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=64), nullable=True),
        sa.Column(
            'source',
            sa.Enum('manual', 'hubspot', 'excel_upload', name='prospect_source_enum'),
            nullable=False,
            server_default='manual',
        ),
        sa.Column(
            'status',
            sa.Enum(
                'pending', 'crawling', 'auditing', 'scoring', 'generating_report', 'completed', 'failed', 'moderation_flagged',
                name='prospect_status_enum'
            ),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('hubspot_id', sa.String(length=128), nullable=True),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batch_jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_prospects_domain'), 'prospects', ['domain'], unique=False)
    op.create_index(op.f('ix_prospects_status'), 'prospects', ['status'], unique=False)
    op.create_index(op.f('ix_prospects_hubspot_id'), 'prospects', ['hubspot_id'], unique=False)
    op.create_index(op.f('ix_prospects_batch_id'), 'prospects', ['batch_id'], unique=False)
    op.create_index('idx_prospect_domain_source', 'prospects', ['domain', 'source'], unique=False)

    # 3. Score Results Table
    op.create_table(
        'score_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prospect_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('seo_score', sa.Float(), nullable=True),
        sa.Column('lead_gen_score', sa.Float(), nullable=True),
        sa.Column('ui_ux_score', sa.Float(), nullable=True),
        sa.Column('broken_links_score', sa.Float(), nullable=True),
        sa.Column('category_weights', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('critical_focus_areas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('pagespeed_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('semrush_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('crawler_lead_gen_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('crawler_broken_links_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('crawler_ui_ux_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prospect_id'], ['prospects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prospect_id'),
    )
    op.create_index(op.f('ix_score_results_prospect_id'), 'score_results', ['prospect_id'], unique=True)

    # 4. Rating Flags Table (Automated Content Moderation)
    op.create_table(
        'rating_flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prospect_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column(
            'flag_category',
            sa.Enum('adult_content', 'political_content', 'under_construction', 'parked_domain', 'gambling', 'malicious', 'other', name='flag_category_enum'),
            nullable=False,
            server_default='other',
        ),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('reason', sa.String(length=512), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_reviewed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_override_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prospect_id'], ['prospects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rating_flags_prospect_id'), 'rating_flags', ['prospect_id'], unique=False)

    # 5. Reports Table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prospect_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score_result_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'report_format',
            sa.Enum('pdf', 'docx', 'html', name='report_format_enum'),
            nullable=False,
            server_default='pdf',
        ),
        sa.Column(
            'status',
            sa.Enum('generating', 'ready', 'failed', name='report_status_enum'),
            nullable=False,
            server_default='generating',
        ),
        sa.Column('file_path', sa.String(length=512), nullable=True),
        sa.Column('file_url', sa.String(length=512), nullable=True),
        sa.Column('logo_url', sa.String(length=512), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('generation_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('html_preview_cache', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prospect_id'], ['prospects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['score_result_id'], ['score_results.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reports_prospect_id'), 'reports', ['prospect_id'], unique=False)
    op.create_index(op.f('ix_reports_score_result_id'), 'reports', ['score_result_id'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('rating_flags')
    op.drop_table('score_results')
    op.drop_table('prospects')
    op.drop_table('batch_jobs')

    op.execute('DROP TYPE IF EXISTS report_status_enum')
    op.execute('DROP TYPE IF EXISTS report_format_enum')
    op.execute('DROP TYPE IF EXISTS flag_category_enum')
    op.execute('DROP TYPE IF EXISTS prospect_status_enum')
    op.execute('DROP TYPE IF EXISTS prospect_source_enum')
    op.execute('DROP TYPE IF EXISTS batch_status_enum')
    op.execute('DROP TYPE IF EXISTS batch_source_enum')
