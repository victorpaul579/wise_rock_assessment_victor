"""create api staging tables

Revision ID: 2b8d9e6c1a4f
Revises: 57c1110b92dd
Create Date: 2025-06-24 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2b8d9e6c1a4f'
down_revision: Union[str, Sequence[str], None] = '57c1110b92dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Creates all staging tables for the API data sources based on direct API evidence."""
    
    # ==============================================================================
    # Aries Data
    # ============================================================================== okay I will mention and I need to resume my according to this requirement
    op.create_table('stg_aries__daily_capacities',
        sa.Column('well_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('oil', sa.Numeric(), nullable=True),
        sa.Column('gas', sa.Numeric(), nullable=True),
        sa.Column('water', sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint('well_id', 'date', name='pk_aries_daily_capacities')
    )

    # ==============================================================================
    # ProCount Data
    # ==============================================================================
    op.create_table('stg_pro_count__completiondailytb',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('merrickid', sa.Integer(), nullable=True),
        sa.Column('recorddate', sa.DateTime(), nullable=True),
        sa.Column('productiondate', sa.DateTime(), nullable=True),
        sa.Column('producingmethod', sa.Integer(), nullable=True),
        sa.Column('dailydowntime', sa.Numeric(), nullable=True),
        sa.Column('allocestoilvol', sa.Numeric(), nullable=True),
        sa.Column('oilproduction', sa.Numeric(), nullable=True),
        sa.Column('allocestgasvolmcf', sa.Numeric(), nullable=True),
        sa.Column('allocestinjgasvolmcf', sa.Numeric(), nullable=True),
        sa.Column('allocestwatervol', sa.Numeric(), nullable=True),
        sa.Column('waterproduction', sa.Numeric(), nullable=True),
        sa.Column('chokesize', sa.Numeric(), nullable=True),
        sa.Column('casingpressure', sa.Numeric(), nullable=True),
        sa.Column('tubingpressure', sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stg_pro_count__completiondailytb_merrickid_date'), 'stg_pro_count__completiondailytb', ['merrickid', 'productiondate'], unique=False)

    # ==============================================================================
    # WellView Data
    # ==============================================================================
    op.create_table('stg_wellview__wellheader',
        sa.Column('idwell', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('area', sa.String(), nullable=True),
        sa.Column('basin', sa.String(), nullable=True),
        sa.Column('basincode', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('currentwellstatus1', sa.String(), nullable=True),
        sa.Column('district', sa.String(), nullable=True),
        sa.Column('division', sa.String(), nullable=True),
        sa.Column('dttmfirstprod', sa.DateTime(), nullable=True),
        sa.Column('dttmspud', sa.DateTime(), nullable=True),
        sa.Column('fieldname', sa.String(), nullable=True),
        sa.Column('fieldoffice', sa.String(), nullable=True),
        sa.Column('latitude', sa.String(), nullable=True),
        sa.Column('latlongdatum', sa.String(), nullable=True),
        sa.Column('lease', sa.String(), nullable=True),
        sa.Column('longitude', sa.String(), nullable=True),
        sa.Column('operated', sa.String(), nullable=True),
        sa.Column('operator', sa.String(), nullable=True),
        sa.Column('padname', sa.String(), nullable=True),
        sa.Column('stateprov', sa.String(), nullable=True),
        sa.Column('wellconfig', sa.String(), nullable=True),
        sa.Column('wellida', sa.String(), nullable=True),
        sa.Column('wellidb', sa.String(), nullable=True),
        sa.Column('wellidc', sa.String(), nullable=True),
        sa.Column('wellidd', sa.String(), nullable=True),
        sa.Column('wellide', sa.String(), nullable=True),
        sa.Column('wellname', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('idwell')
    )
    
    op.create_table('stg_wellview__job',
        sa.Column('idwell', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('idrec', sa.String(), nullable=False),
        sa.Column('dttmend', sa.String(), nullable=True),
        sa.Column('dttmstart', sa.String(), nullable=True),
        sa.Column('jobsubtyp', sa.String(), nullable=True),
        sa.Column('jobtyp', sa.String(), nullable=True),
        sa.Column('status1', sa.String(), nullable=True),
        sa.Column('status2', sa.String(), nullable=True),
        sa.Column('targetform', sa.String(), nullable=True),
        sa.Column('usertxt1', sa.String(), nullable=True),
        sa.Column('wvtyp', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('idrec'),
        sa.ForeignKeyConstraint(['idwell'], ['stg_wellview__wellheader.idwell'])
    )
    op.create_index(op.f('ix_stg_wellview__job_idwell'), 'stg_wellview__job', ['idwell'], unique=False)

    op.create_table('stg_wellview__jobreport',
        sa.Column('idwell', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('idrecparent', sa.String(), nullable=True),
        sa.Column('idrec', sa.String(), nullable=False),
        sa.Column('condhole', sa.String(), nullable=True),
        sa.Column('condlease', sa.String(), nullable=True),
        sa.Column('condroad', sa.String(), nullable=True),
        sa.Column('condwave', sa.String(), nullable=True),
        sa.Column('condweather', sa.String(), nullable=True),
        sa.Column('condwind', sa.String(), nullable=True),
        sa.Column('depthtvdendprojmethod', sa.String(), nullable=True),
        sa.Column('dttmend', sa.String(), nullable=True),
        sa.Column('dttmstart', sa.String(), nullable=True),
        sa.Column('rigtime', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('idrec'),
        sa.ForeignKeyConstraint(['idwell'], ['stg_wellview__wellheader.idwell']),
        sa.ForeignKeyConstraint(['idrecparent'], ['stg_wellview__job.idrec'])
    )
    op.create_index(op.f('ix_stg_wellview__jobreport_idwell'), 'stg_wellview__jobreport', ['idwell'], unique=False)
    op.create_index(op.f('ix_stg_wellview__jobreport_idrecparent'), 'stg_wellview__jobreport', ['idrecparent'], unique=False)

    op.create_table('stg_wellview__surveypoint',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('well_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('azimuth_deg', sa.Numeric(), nullable=True),
        sa.Column('inclination_deg', sa.Numeric(), nullable=True),
        sa.Column('measured_depth_ft', sa.Numeric(), nullable=True),
        sa.Column('easting_offset_ft', sa.Numeric(), nullable=True),
        sa.Column('northing_offset_ft', sa.Numeric(), nullable=True),
        sa.Column('tvd_offset_ft', sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['well_id'], ['stg_wellview__wellheader.idwell'])
    )
    op.create_index(op.f('ix_stg_wellview__surveypoint_well_id'), 'stg_wellview__surveypoint', ['well_id'], unique=False)

    # ==============================================================================
    # Wise Rock Data
    # ==============================================================================
    op.create_table('stg_wiserock__note',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('event_id', sa.BigInteger(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_overwrite', sa.String(), nullable=True),
        sa.Column('note_timestamp', sa.String(), nullable=True),
        sa.Column('note_text', sa.Text(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True),
        sa.Column('event_uuid', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('note_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stg_wiserock__note_event_uuid'), 'stg_wiserock__note', ['event_uuid'], unique=False)
    op.create_index(op.f('ix_stg_wiserock__note_user_id'), 'stg_wiserock__note', ['user_id'], unique=False)
    op.create_index(op.f('ix_stg_wiserock__note_note_id'), 'stg_wiserock__note', ['note_id'], unique=False)

    op.create_table('stg_wiserock__user',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('handle', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )

    # ==============================================================================
    # EIA Data
    # ==============================================================================
    op.create_table('stg_eia__oil_price',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('period', sa.Date(), nullable=True),
        sa.Column('duoarea', sa.String(), nullable=True),
        sa.Column('area_name', sa.String(), nullable=True),
        sa.Column('product', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('process', sa.String(), nullable=True),
        sa.Column('process_name', sa.String(), nullable=True),
        sa.Column('series', sa.String(), nullable=True),
        sa.Column('series_description', sa.String(), nullable=True),
        sa.Column('value', sa.Numeric(), nullable=True),
        sa.Column('units', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stg_eia__oil_price_period_series'), 'stg_eia__oil_price', ['period', 'series'], unique=True)


def downgrade() -> None:
    """Reverts all changes made in the upgrade function."""
    op.drop_table('stg_eia__oil_price')
    op.drop_table('stg_wiserock__user')
    op.drop_table('stg_wiserock__note')
    op.drop_table('stg_wellview__surveypoint')
    op.drop_table('stg_wellview__jobreport')
    op.drop_table('stg_wellview__job')
    op.drop_table('stg_wellview__wellheader')
    op.drop_table('stg_pro_count__completiondailytb')
    op.drop_table('stg_aries__daily_capacities')

