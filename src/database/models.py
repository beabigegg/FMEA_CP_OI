from sqlalchemy import Column, Integer, String, Enum, JSON, TIMESTAMP, ForeignKey, UniqueConstraint, TEXT, DATE
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class Document(Base):
    __tablename__ = 'fmcp_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    document_type = Column(Enum('FMEA', 'CP', 'OI'), nullable=False)
    version = Column(String(50), default='1.0')
    uploaded_by = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    fmea_header = relationship('FmeaHeader', back_populates='document', uselist=False, cascade='all, delete-orphan')
    fmea_items = relationship('FmeaItem', back_populates='document', cascade='all, delete-orphan')
    fmea_fe_items = relationship('FmeaFeItem', back_populates='document', cascade='all, delete-orphan')
    cp_items = relationship('CpItem', back_populates='document', cascade='all, delete-orphan')


class FmeaHeader(Base):
    __tablename__ = 'fmcp_fmea_header'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('fmcp_documents.id', ondelete='CASCADE'), nullable=False)
    company_name = Column(String(255), default=None)
    customer_name = Column(String(255), default=None)
    model_year_platform = Column(String(255), default=None)
    plant_location = Column(String(255), default=None)
    subject = Column(String(255), default=None)
    pfmea_start_date = Column(DATE, default=None)
    pfmea_revision_date = Column(DATE, default=None)
    pfmea_id = Column(String(50), default=None)
    process_responsibility = Column(String(255), default=None)
    cross_functional_team = Column(String(255), default=None)
    confidentiality_level = Column(String(100), default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    document = relationship('Document', back_populates='fmea_header')


class FmeaItem(Base):
    __tablename__ = 'fmcp_fmea_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('fmcp_documents.id', ondelete='CASCADE'), nullable=False)
    row_index = Column(Integer, comment='Original row number from the source file for reference')
    process_step = Column(TEXT)
    failure_mode = Column(TEXT)
    failure_cause = Column(TEXT)
    detection_controls = Column(TEXT)
    severity = Column(TINYINT)
    occurrence = Column(TINYINT)
    detection = Column(TINYINT)
    ap = Column(Enum('H', 'M', 'L'), comment='Action Priority')
    issue_no = Column(TEXT)
    history_change_authorization = Column(TEXT)
    process_item = Column(TEXT)
    process_work_element = Column(TEXT)
    function_of_process_item = Column(TEXT)
    function_of_process_step_and_product_characteristic = Column(TEXT)
    function_of_process_work_element_and_process_characteristic = Column(TEXT)
    failure_effects_description = Column(TEXT)
    prevention_controls_description = Column(TEXT)
    special_characteristics = Column(TEXT)
    filter_code = Column(TEXT)
    prevention_action = Column(TEXT)
    detection_action = Column(TEXT)
    responsible_person_name = Column(TEXT)
    target_completion_date = Column(TEXT)
    status = Column(TEXT)
    action_taken = Column(TEXT)
    completion_date = Column(TEXT)
    severity_opt = Column(TINYINT)
    occurrence_opt = Column(TINYINT)
    detection_opt = Column(TINYINT)
    ap_opt = Column(Enum('H', 'M', 'L'))
    remarks = Column(TEXT)
    special_characteristics_opt = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    document = relationship('Document', back_populates='fmea_items')


class FmeaFeItem(Base):
    __tablename__ = 'fmcp_fmea_fe_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('fmcp_documents.id', ondelete='CASCADE'), nullable=False)
    failure_effect = Column(TEXT)
    severity = Column(TINYINT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    document = relationship('Document', back_populates='fmea_fe_items')


class CpItem(Base):
    __tablename__ = 'fmcp_cp_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('fmcp_documents.id', ondelete='CASCADE'), nullable=False)
    row_index = Column(Integer, comment='Original row number from the source file for reference')
    process_name = Column(TEXT)
    product_characteristic = Column(TEXT)
    process_characteristic = Column(TEXT)
    evaluation_technique = Column(TEXT)
    control_method = Column(TEXT)
    spec_tolerance = Column(TEXT)
    sample_size = Column(String(50))
    sample_freq = Column(String(50))
    special_character_class = Column(String(100))
    equipment = Column(TEXT)
    reaction_plan = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    document = relationship('Document', back_populates='cp_items')


class Association(Base):
    __tablename__ = 'fmcp_associations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fmea_item_id = Column(Integer, ForeignKey('fmcp_fmea_items.id', ondelete='CASCADE'), nullable=False)
    cp_item_id = Column(Integer, ForeignKey('fmcp_cp_items.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (UniqueConstraint('fmea_item_id', 'cp_item_id', name='_fmea_cp_uc'),)

    fmea_item = relationship('FmeaItem', foreign_keys=[fmea_item_id])
    cp_item = relationship('CpItem', foreign_keys=[cp_item_id])


class User(Base):
    __tablename__ = 'fmcp_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default='editor')
    created_at = Column(TIMESTAMP, server_default=func.now())
