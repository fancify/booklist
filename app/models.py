"""
三层书单数据模型

1. RawBooklist - 原始书单（爬取的原始数据）
2. Booklist - 书单层（按人物/来源汇总，自动去重）
3. MetaBooklist - 元书单（用户自定义，多个Booklist合并，按频次排序）
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# ============ 书籍（全局唯一）============
class Book(Base):
    """标准化后的书籍，全局唯一"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), unique=True, nullable=True, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(200), nullable=True)
    cover_url = Column(String(500), nullable=True)
    douban_id = Column(String(20), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============ 第一层：原始书单 ============
class RawBooklist(Base):
    """原始书单 - 直接从网上爬取的书单"""
    __tablename__ = "raw_booklists"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)  # 如 "比尔·盖茨2023年度推荐"
    source_url = Column(String(500), nullable=True)  # 来源URL
    booklist_id = Column(Integer, ForeignKey("booklists.id"), nullable=True)  # 归属的Booklist
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    booklist = relationship("Booklist", back_populates="raw_booklists")
    items = relationship("RawBooklistItem", back_populates="raw_booklist", cascade="all, delete-orphan")


class RawBooklistItem(Base):
    """原始书单中的书籍条目"""
    __tablename__ = "raw_booklist_items"

    id = Column(Integer, primary_key=True)
    raw_booklist_id = Column(Integer, ForeignKey("raw_booklists.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    rank = Column(Integer, nullable=True)  # 在原书单中的排名

    # 关系
    raw_booklist = relationship("RawBooklist", back_populates="items")
    book = relationship("Book")


# ============ 第二层：书单层 ============
class Booklist(Base):
    """书单层 - 汇总同一来源的多个原始书单，自动去重"""
    __tablename__ = "booklists"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)  # 如 "比尔·盖茨推荐书单"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    raw_booklists = relationship("RawBooklist", back_populates="booklist")


# ============ 第三层：元书单 ============
# MetaBooklist 与 Booklist 的多对多关系
meta_booklist_booklists = Table(
    "meta_booklist_booklists",
    Base.metadata,
    Column("meta_booklist_id", Integer, ForeignKey("meta_booklists.id"), primary_key=True),
    Column("booklist_id", Integer, ForeignKey("booklists.id"), primary_key=True),
)


class MetaBooklist(Base):
    """元书单 - 用户自定义，合并多个Booklist，按出现频次排序"""
    __tablename__ = "meta_booklists"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)  # 如 "科技大佬推荐"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系：包含哪些Booklist
    booklists = relationship("Booklist", secondary=meta_booklist_booklists)


class MetaBooklistResult(Base):
    """元书单的计算结果 - 按频次排序的书籍"""
    __tablename__ = "meta_booklist_results"

    id = Column(Integer, primary_key=True)
    meta_booklist_id = Column(Integer, ForeignKey("meta_booklists.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    frequency = Column(Integer, nullable=False)  # 出现次数
    rank = Column(Integer, nullable=False)  # 排名

    # 关系
    meta_booklist = relationship("MetaBooklist")
    book = relationship("Book")
