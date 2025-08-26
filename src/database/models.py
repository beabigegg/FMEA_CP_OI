from sqlalchemy import Column, Integer, String, Enum, JSON, TIMESTAMP, ForeignKey, UniqueConstraint
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

    items = relationship('Item', back_populates='document', cascade='all, delete-orphan')

class Item(Base):
    __tablename__ = 'fmcp_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('fmcp_documents.id', ondelete='CASCADE'), nullable=False)
    row_index = Column(Integer, comment='Original row number from the source file for reference')
    content = Column(JSON, nullable=False)
    edited_by = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    document = relationship('Document', back_populates='items')

class Association(Base):
    __tablename__ = 'fmcp_associations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fmea_item_id = Column(Integer, ForeignKey('fmcp_items.id', ondelete='CASCADE'), nullable=False)
    cp_item_id = Column(Integer, ForeignKey('fmcp_items.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (UniqueConstraint('fmea_item_id', 'cp_item_id', name='_fmea_cp_uc'),)

    # [FIX] Add relationships to fetch the actual Item objects
    # We must specify foreign_keys because there are two FKs to the same Item table
    fmea_item = relationship('Item', foreign_keys=[fmea_item_id])
    cp_item = relationship('Item', foreign_keys=[cp_item_id])


class ItemHistory(Base):
    __tablename__ = 'fmcp_item_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('fmcp_items.id', ondelete='CASCADE'), nullable=False)
    old_content = Column(JSON, nullable=True)
    new_content = Column(JSON, nullable=False)
    change_type = Column(Enum('CREATE', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = Column(String(100), nullable=False)
    changed_at = Column(TIMESTAMP, server_default=func.now())

    item = relationship('Item')

class User(Base):
    __tablename__ = 'fmcp_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default='editor')
    created_at = Column(TIMESTAMP, server_default=func.now())