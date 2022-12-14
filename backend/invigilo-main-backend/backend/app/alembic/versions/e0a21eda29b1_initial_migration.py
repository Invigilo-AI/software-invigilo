"""Initial migration

Revision ID: e0a21eda29b1
Revises: 
Create Date: 2022-04-01 15:01:29.471729

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = 'e0a21eda29b1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ai_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('index', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_type_created_at'), 'ai_type', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_type_deleted'), 'ai_type', ['deleted'], unique=False)
    op.create_index(op.f('ix_ai_type_id'), 'ai_type', ['id'], unique=False)
    op.create_index(op.f('ix_ai_type_index'), 'ai_type', ['index'], unique=True)
    op.create_index(op.f('ix_ai_type_updated_at'), 'ai_type', ['updated_at'], unique=False)
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('logo', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_created_at'), 'company', ['created_at'], unique=False)
    op.create_index(op.f('ix_company_deleted'), 'company', ['deleted'], unique=False)
    op.create_index(op.f('ix_company_id'), 'company', ['id'], unique=False)
    op.create_index(op.f('ix_company_name'), 'company', ['name'], unique=False)
    op.create_index(op.f('ix_company_updated_at'), 'company', ['updated_at'], unique=False)
    op.create_table('ai_sequence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_sequence_company_id'), 'ai_sequence', ['company_id'], unique=False)
    op.create_index(op.f('ix_ai_sequence_created_at'), 'ai_sequence', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_sequence_deleted'), 'ai_sequence', ['deleted'], unique=False)
    op.create_index(op.f('ix_ai_sequence_id'), 'ai_sequence', ['id'], unique=False)
    op.create_index(op.f('ix_ai_sequence_updated_at'), 'ai_sequence', ['updated_at'], unique=False)
    op.create_table('ai_server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('connection', sa.String(), nullable=True),
    sa.Column('vertex_types', sqlalchemy_utils.types.scalar_list.ScalarListType(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_live', sa.Boolean(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_server_company_id'), 'ai_server', ['company_id'], unique=False)
    op.create_index(op.f('ix_ai_server_connection'), 'ai_server', ['connection'], unique=False)
    op.create_index(op.f('ix_ai_server_created_at'), 'ai_server', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_server_deleted'), 'ai_server', ['deleted'], unique=False)
    op.create_index(op.f('ix_ai_server_id'), 'ai_server', ['id'], unique=False)
    op.create_index(op.f('ix_ai_server_location'), 'ai_server', ['location'], unique=False)
    op.create_index(op.f('ix_ai_server_name'), 'ai_server', ['name'], unique=False)
    op.create_index(op.f('ix_ai_server_updated_at'), 'ai_server', ['updated_at'], unique=False)
    op.create_table('cam_server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('connection', sa.String(), nullable=True),
    sa.Column('access_token', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_live', sa.Boolean(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cam_server_access_token'), 'cam_server', ['access_token'], unique=True)
    op.create_index(op.f('ix_cam_server_company_id'), 'cam_server', ['company_id'], unique=False)
    op.create_index(op.f('ix_cam_server_connection'), 'cam_server', ['connection'], unique=False)
    op.create_index(op.f('ix_cam_server_created_at'), 'cam_server', ['created_at'], unique=False)
    op.create_index(op.f('ix_cam_server_deleted'), 'cam_server', ['deleted'], unique=False)
    op.create_index(op.f('ix_cam_server_id'), 'cam_server', ['id'], unique=False)
    op.create_index(op.f('ix_cam_server_location'), 'cam_server', ['location'], unique=False)
    op.create_index(op.f('ix_cam_server_name'), 'cam_server', ['name'], unique=False)
    op.create_index(op.f('ix_cam_server_updated_at'), 'cam_server', ['updated_at'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('permissions', sqlalchemy_utils.types.scalar_list.ScalarListType(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_created_at'), 'user', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_deleted'), 'user', ['deleted'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=False)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_updated_at'), 'user', ['updated_at'], unique=False)
    op.create_table('ai_vertex',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('types', sqlalchemy_utils.types.scalar_list.ScalarListType(), nullable=True),
    sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.Column('sequence_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sequence_id'], ['ai_sequence.id'], ),
    sa.ForeignKeyConstraint(['server_id'], ['ai_server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_vertex_created_at'), 'ai_vertex', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_vertex_deleted'), 'ai_vertex', ['deleted'], unique=False)
    op.create_index(op.f('ix_ai_vertex_id'), 'ai_vertex', ['id'], unique=False)
    op.create_index(op.f('ix_ai_vertex_sequence_id'), 'ai_vertex', ['sequence_id'], unique=False)
    op.create_index(op.f('ix_ai_vertex_server_id'), 'ai_vertex', ['server_id'], unique=False)
    op.create_index(op.f('ix_ai_vertex_updated_at'), 'ai_vertex', ['updated_at'], unique=False)
    op.create_table('camera',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('connection', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_live', sa.Boolean(), nullable=True),
    sa.Column('cam_server_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cam_server_id'], ['cam_server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_camera_cam_server_id'), 'camera', ['cam_server_id'], unique=False)
    op.create_index(op.f('ix_camera_created_at'), 'camera', ['created_at'], unique=False)
    op.create_index(op.f('ix_camera_deleted'), 'camera', ['deleted'], unique=False)
    op.create_index(op.f('ix_camera_id'), 'camera', ['id'], unique=False)
    op.create_index(op.f('ix_camera_name'), 'camera', ['name'], unique=False)
    op.create_index(op.f('ix_camera_updated_at'), 'camera', ['updated_at'], unique=False)
    op.create_table('ai_edge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('sequence_id', sa.Integer(), nullable=True),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('destination_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['destination_id'], ['ai_vertex.id'], ),
    sa.ForeignKeyConstraint(['sequence_id'], ['ai_sequence.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['ai_vertex.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_edge_created_at'), 'ai_edge', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_edge_deleted'), 'ai_edge', ['deleted'], unique=False)
    op.create_index(op.f('ix_ai_edge_destination_id'), 'ai_edge', ['destination_id'], unique=False)
    op.create_index(op.f('ix_ai_edge_id'), 'ai_edge', ['id'], unique=False)
    op.create_index(op.f('ix_ai_edge_sequence_id'), 'ai_edge', ['sequence_id'], unique=False)
    op.create_index(op.f('ix_ai_edge_source_id'), 'ai_edge', ['source_id'], unique=False)
    op.create_index(op.f('ix_ai_edge_updated_at'), 'ai_edge', ['updated_at'], unique=False)
    op.create_table('cam_ai_mapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('meta', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('sequence_id', sa.Integer(), nullable=True),
    sa.Column('camera_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['camera_id'], ['camera.id'], ),
    sa.ForeignKeyConstraint(['sequence_id'], ['ai_sequence.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cam_ai_mapping_camera_id'), 'cam_ai_mapping', ['camera_id'], unique=False)
    op.create_index(op.f('ix_cam_ai_mapping_created_at'), 'cam_ai_mapping', ['created_at'], unique=False)
    op.create_index(op.f('ix_cam_ai_mapping_deleted'), 'cam_ai_mapping', ['deleted'], unique=False)
    op.create_index(op.f('ix_cam_ai_mapping_id'), 'cam_ai_mapping', ['id'], unique=False)
    op.create_index(op.f('ix_cam_ai_mapping_sequence_id'), 'cam_ai_mapping', ['sequence_id'], unique=False)
    op.create_index(op.f('ix_cam_ai_mapping_updated_at'), 'cam_ai_mapping', ['updated_at'], unique=False)
    op.create_table('cam_frame',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('duration', sa.Interval(), nullable=True),
    sa.Column('camera_id', sa.Integer(), nullable=True),
    sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('video', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['camera_id'], ['camera.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cam_frame_camera_id'), 'cam_frame', ['camera_id'], unique=False)
    op.create_index(op.f('ix_cam_frame_created_at'), 'cam_frame', ['created_at'], unique=False)
    op.create_index(op.f('ix_cam_frame_deleted'), 'cam_frame', ['deleted'], unique=False)
    op.create_index(op.f('ix_cam_frame_id'), 'cam_frame', ['id'], unique=False)
    op.create_index(op.f('ix_cam_frame_updated_at'), 'cam_frame', ['updated_at'], unique=False)
    op.create_table('incident',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('type', sqlalchemy_utils.types.scalar_list.ScalarListType(), nullable=True),
    sa.Column('ai_mapping_id', sa.Integer(), nullable=True),
    sa.Column('camera_id', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('acknowledged', sa.DateTime(), nullable=True),
    sa.Column('inaccurate', sa.Boolean(), nullable=True),
    sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('frame', sa.String(), nullable=True),
    sa.Column('video', sa.String(), nullable=True),
    sa.Column('people', sa.Integer(), nullable=True),
    sa.Column('objects', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ai_mapping_id'], ['cam_ai_mapping.id'], ),
    sa.ForeignKeyConstraint(['camera_id'], ['camera.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_ai_mapping_id'), 'incident', ['ai_mapping_id'], unique=False)
    op.create_index(op.f('ix_incident_camera_id'), 'incident', ['camera_id'], unique=False)
    op.create_index(op.f('ix_incident_created_at'), 'incident', ['created_at'], unique=False)
    op.create_index(op.f('ix_incident_deleted'), 'incident', ['deleted'], unique=False)
    op.create_index(op.f('ix_incident_id'), 'incident', ['id'], unique=False)
    op.create_index(op.f('ix_incident_type'), 'incident', ['type'], unique=False)
    op.create_index(op.f('ix_incident_updated_at'), 'incident', ['updated_at'], unique=False)
    op.create_index(op.f('ix_incident_uuid'), 'incident', ['uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_incident_uuid'), table_name='incident')
    op.drop_index(op.f('ix_incident_updated_at'), table_name='incident')
    op.drop_index(op.f('ix_incident_type'), table_name='incident')
    op.drop_index(op.f('ix_incident_id'), table_name='incident')
    op.drop_index(op.f('ix_incident_deleted'), table_name='incident')
    op.drop_index(op.f('ix_incident_created_at'), table_name='incident')
    op.drop_index(op.f('ix_incident_camera_id'), table_name='incident')
    op.drop_index(op.f('ix_incident_ai_mapping_id'), table_name='incident')
    op.drop_table('incident')
    op.drop_index(op.f('ix_cam_frame_updated_at'), table_name='cam_frame')
    op.drop_index(op.f('ix_cam_frame_id'), table_name='cam_frame')
    op.drop_index(op.f('ix_cam_frame_deleted'), table_name='cam_frame')
    op.drop_index(op.f('ix_cam_frame_created_at'), table_name='cam_frame')
    op.drop_index(op.f('ix_cam_frame_camera_id'), table_name='cam_frame')
    op.drop_table('cam_frame')
    op.drop_index(op.f('ix_cam_ai_mapping_updated_at'), table_name='cam_ai_mapping')
    op.drop_index(op.f('ix_cam_ai_mapping_sequence_id'), table_name='cam_ai_mapping')
    op.drop_index(op.f('ix_cam_ai_mapping_id'), table_name='cam_ai_mapping')
    op.drop_index(op.f('ix_cam_ai_mapping_deleted'), table_name='cam_ai_mapping')
    op.drop_index(op.f('ix_cam_ai_mapping_created_at'), table_name='cam_ai_mapping')
    op.drop_index(op.f('ix_cam_ai_mapping_camera_id'), table_name='cam_ai_mapping')
    op.drop_table('cam_ai_mapping')
    op.drop_index(op.f('ix_ai_edge_updated_at'), table_name='ai_edge')
    op.drop_index(op.f('ix_ai_edge_source_id'), table_name='ai_edge')
    op.drop_index(op.f('ix_ai_edge_sequence_id'), table_name='ai_edge')
    op.drop_index(op.f('ix_ai_edge_id'), table_name='ai_edge')
    op.drop_index(op.f('ix_ai_edge_destination_id'), table_name='ai_edge')
    op.drop_index(op.f('ix_ai_edge_deleted'), table_name='ai_edge')
    op.drop_index(op.f('ix_ai_edge_created_at'), table_name='ai_edge')
    op.drop_table('ai_edge')
    op.drop_index(op.f('ix_camera_updated_at'), table_name='camera')
    op.drop_index(op.f('ix_camera_name'), table_name='camera')
    op.drop_index(op.f('ix_camera_id'), table_name='camera')
    op.drop_index(op.f('ix_camera_deleted'), table_name='camera')
    op.drop_index(op.f('ix_camera_created_at'), table_name='camera')
    op.drop_index(op.f('ix_camera_cam_server_id'), table_name='camera')
    op.drop_table('camera')
    op.drop_index(op.f('ix_ai_vertex_updated_at'), table_name='ai_vertex')
    op.drop_index(op.f('ix_ai_vertex_server_id'), table_name='ai_vertex')
    op.drop_index(op.f('ix_ai_vertex_sequence_id'), table_name='ai_vertex')
    op.drop_index(op.f('ix_ai_vertex_id'), table_name='ai_vertex')
    op.drop_index(op.f('ix_ai_vertex_deleted'), table_name='ai_vertex')
    op.drop_index(op.f('ix_ai_vertex_created_at'), table_name='ai_vertex')
    op.drop_table('ai_vertex')
    op.drop_index(op.f('ix_user_updated_at'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_deleted'), table_name='user')
    op.drop_index(op.f('ix_user_created_at'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_cam_server_updated_at'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_name'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_location'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_id'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_deleted'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_created_at'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_connection'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_company_id'), table_name='cam_server')
    op.drop_index(op.f('ix_cam_server_access_token'), table_name='cam_server')
    op.drop_table('cam_server')
    op.drop_index(op.f('ix_ai_server_updated_at'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_name'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_location'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_id'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_deleted'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_created_at'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_connection'), table_name='ai_server')
    op.drop_index(op.f('ix_ai_server_company_id'), table_name='ai_server')
    op.drop_table('ai_server')
    op.drop_index(op.f('ix_ai_sequence_updated_at'), table_name='ai_sequence')
    op.drop_index(op.f('ix_ai_sequence_id'), table_name='ai_sequence')
    op.drop_index(op.f('ix_ai_sequence_deleted'), table_name='ai_sequence')
    op.drop_index(op.f('ix_ai_sequence_created_at'), table_name='ai_sequence')
    op.drop_index(op.f('ix_ai_sequence_company_id'), table_name='ai_sequence')
    op.drop_table('ai_sequence')
    op.drop_index(op.f('ix_company_updated_at'), table_name='company')
    op.drop_index(op.f('ix_company_name'), table_name='company')
    op.drop_index(op.f('ix_company_id'), table_name='company')
    op.drop_index(op.f('ix_company_deleted'), table_name='company')
    op.drop_index(op.f('ix_company_created_at'), table_name='company')
    op.drop_table('company')
    op.drop_index(op.f('ix_ai_type_updated_at'), table_name='ai_type')
    op.drop_index(op.f('ix_ai_type_index'), table_name='ai_type')
    op.drop_index(op.f('ix_ai_type_id'), table_name='ai_type')
    op.drop_index(op.f('ix_ai_type_deleted'), table_name='ai_type')
    op.drop_index(op.f('ix_ai_type_created_at'), table_name='ai_type')
    op.drop_table('ai_type')
    # ### end Alembic commands ###
