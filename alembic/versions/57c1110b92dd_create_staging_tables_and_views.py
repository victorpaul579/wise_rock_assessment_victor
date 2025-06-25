"""create staging tables and views

Revision ID: 57c1110b92dd
Revises: 
Create Date: 2025-06-23 14:30:44.841463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57c1110b92dd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Creates all staging tables for the assessment in the public schema."""
    
    # NOTE: We are creating tables in the default 'public' schema
    # because the provided user does not have permission to create new schemas.

    # ==============================================================================
    # Dimension / Lookup Tables
    # ==============================================================================

    op.create_table(
        'stg_pro_count__areatb',
        sa.Column('areamerrickid', sa.Integer, primary_key=True),
        sa.Column('areaname', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__batterytb',
        sa.Column('batterymerrickid', sa.Integer, primary_key=True),
        sa.Column('batteryname', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__divisiontb',
        sa.Column('divisionmerrickid', sa.Integer, primary_key=True),
        sa.Column('divisionname', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__fieldgrouptb',
        sa.Column('fieldgroupmerrickid', sa.Integer, primary_key=True),
        sa.Column('fieldgroupname', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__producingmethodstb',
        sa.Column('producingmethodsmerrickid', sa.Integer, primary_key=True),
        sa.Column('producingmethodsdescription', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__producingstatustb',
        sa.Column('producingstatusmerrickid', sa.Integer, primary_key=True),
        sa.Column('producingdescription', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__routetb',
        sa.Column('routemerrickid', sa.Integer, primary_key=True),
        sa.Column('routename', sa.String(255))
    )

    op.create_table(
        'stg_pro_count__statecountynamestb',
        sa.Column('statecode', sa.Integer, nullable=False),
        sa.Column('countycode', sa.Integer, nullable=False),
        sa.Column('countyname', sa.String(255)),
        sa.PrimaryKeyConstraint('statecode', 'countycode')
    )

    # ==============================================================================
    # Aries Property Table
    # ==============================================================================
    
    op.create_table(
        'stg_aries__ac_property',
        sa.Column('propnum', sa.String(64), primary_key=True),
        sa.Column('allocid', sa.Integer),
        sa.Column('propname', sa.String(255)),
        sa.Column('apinum', sa.BigInteger),
        sa.Column('nri', sa.Numeric(18, 10)),
    )
    op.create_index(op.f('ix_stg_aries__ac_property_allocid'), 'stg_aries__ac_property', ['allocid'], unique=False)
    op.create_index(op.f('ix_stg_aries__ac_property_apinum'), 'stg_aries__ac_property', ['apinum'], unique=False)

    # ==============================================================================
    # Main Fact Table: Completion
    # ==============================================================================

    op.create_table(
        'stg_pro_count__completiontb',
        sa.Column('merrickid', sa.Integer, primary_key=True),
        sa.Column('wellname', sa.String(255)),
        sa.Column('completiontype', sa.Integer),
        sa.Column('producingstatus', sa.Integer),
        sa.Column('producingmethod', sa.Integer),
        sa.Column('apiwellnumber', sa.BigInteger),
        sa.Column('routeid', sa.Integer),
        sa.Column('groupid', sa.Integer),
        sa.Column('divisionid', sa.Integer),
        sa.Column('fieldgroupid', sa.Integer),
        sa.Column('areaid', sa.Integer),
        sa.Column('batteryid', sa.Integer),
        sa.Column('stateid', sa.Integer),
        sa.Column('countyid', sa.Integer),
        sa.Column('ariesid', sa.String(64)),
        sa.Column('wellviewid', sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column('activeflag', sa.Boolean),
        sa.Column('mmsapiwellnumber', sa.BigInteger),

        # Foreign Key Constraints
        sa.ForeignKeyConstraint(['producingstatus'], ['stg_pro_count__producingstatustb.producingstatusmerrickid']),
        sa.ForeignKeyConstraint(['producingmethod'], ['stg_pro_count__producingmethodstb.producingmethodsmerrickid']),
        sa.ForeignKeyConstraint(['routeid'], ['stg_pro_count__routetb.routemerrickid']),
        sa.ForeignKeyConstraint(['divisionid'], ['stg_pro_count__divisiontb.divisionmerrickid']),
        sa.ForeignKeyConstraint(['fieldgroupid'], ['stg_pro_count__fieldgrouptb.fieldgroupmerrickid']),
        sa.ForeignKeyConstraint(['areaid'], ['stg_pro_count__areatb.areamerrickid']),
        sa.ForeignKeyConstraint(['batteryid'], ['stg_pro_count__batterytb.batterymerrickid']),
        sa.ForeignKeyConstraint(['ariesid'], ['stg_aries__ac_property.propnum']),
        sa.ForeignKeyConstraint(['stateid', 'countyid'], ['stg_pro_count__statecountynamestb.statecode', 'stg_pro_count__statecountynamestb.countycode']),

    )
    
    # Indexes for Foreign Keys - CRITICAL FOR PERFORMANCE
    op.create_index(op.f('ix_stg_pro_count__completiontb_producingstatus'), 'stg_pro_count__completiontb', ['producingstatus'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_producingmethod'), 'stg_pro_count__completiontb', ['producingmethod'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_routeid'), 'stg_pro_count__completiontb', ['routeid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_divisionid'), 'stg_pro_count__completiontb', ['divisionid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_fieldgroupid'), 'stg_pro_count__completiontb', ['fieldgroupid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_areaid'), 'stg_pro_count__completiontb', ['areaid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_batteryid'), 'stg_pro_count__completiontb', ['batteryid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_ariesid'), 'stg_pro_count__completiontb', ['ariesid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_state_county'), 'stg_pro_count__completiontb', ['stateid', 'countyid'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_apiwellnumber'), 'stg_pro_count__completiontb', ['apiwellnumber'], unique=False)
    op.create_index(op.f('ix_stg_pro_count__completiontb_wellviewid'), 'stg_pro_count__completiontb', ['wellviewid'], unique=False)

def downgrade() -> None:
    """Reverts all changes made in the upgrade function."""
    
    # Drop tables in reverse order of creation to respect foreign key dependencies
    op.drop_table('stg_pro_count__completiontb')
    op.drop_table('stg_aries__ac_property')
    op.drop_table('stg_pro_count__statecountynamestb')
    op.drop_table('stg_pro_count__routetb')
    op.drop_table('stg_pro_count__producingstatustb')
    op.drop_table('stg_pro_count__producingmethodstb')
    op.drop_table('stg_pro_count__fieldgrouptb')
    op.drop_table('stg_pro_count__divisiontb')
    op.drop_table('stg_pro_count__batterytb')
    op.drop_table('stg_pro_count__areatb')
