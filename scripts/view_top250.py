#!/usr/bin/env python3
"""查看豆瓣 Top 250 书籍"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Book, RawBooklist, RawBooklistItem
from sqlalchemy import desc


def view_top250(start=1, end=20, show_all=False):
    """查看豆瓣 Top 250 书籍
    
    Args:
        start: 起始排名（从1开始）
        end: 结束排名
        show_all: 是否显示所有书籍
    """
    db = SessionLocal()
    
    try:
        # 查找豆瓣 Top 250 的原始书单
        raw_booklist = db.query(RawBooklist).filter(
            RawBooklist.name == "豆瓣图书 Top 250"
        ).first()
        
        if not raw_booklist:
            print("未找到豆瓣 Top 250 数据，请先运行 scripts/scrape_top250.py")
            return
        
        # 查询所有书籍条目，按排名排序
        items = db.query(RawBooklistItem).filter(
            RawBooklistItem.raw_booklist_id == raw_booklist.id
        ).order_by(RawBooklistItem.rank).all()
        
        print("=" * 100)
        print(f"豆瓣图书 Top 250")
        print(f"原始书单ID: {raw_booklist.id}")
        print(f"来源: {raw_booklist.source_url}")
        print(f"总计: {len(items)} 本书")
        print("=" * 100)
        print()
        
        # 确定显示范围
        if show_all:
            display_items = items
            print(f"全部 {len(items)} 本书：")
        else:
            display_items = [item for item in items if start <= item.rank <= end]
            print(f"排名 #{start} - #{end}：")
        
        print("-" * 100)
        for item in display_items:
            book = item.book
            title = book.title[:60] if len(book.title) > 60 else book.title
            author = (book.author or '未知')[:30]
            douban_id = book.douban_id or 'N/A'
            print(f"#{item.rank:3d} | {title:<60} | {author:<30} | ID: {douban_id}")
        
        if not show_all and len(items) > end:
            print(f"\n... 还有 {len(items) - end} 本书（使用 --all 查看全部）")
        
        # 统计信息
        print("\n" + "=" * 100)
        print("统计信息：")
        print(f"  - 总书籍数: {len(items)}")
        print(f"  - 有作者信息: {sum(1 for item in items if item.book.author)}")
        print(f"  - 有封面: {sum(1 for item in items if item.book.cover_url)}")
        print(f"  - 有豆瓣ID: {sum(1 for item in items if item.book.douban_id)}")
        
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查看豆瓣 Top 250 书籍")
    parser.add_argument("--start", type=int, default=1, help="起始排名（默认：1）")
    parser.add_argument("--end", type=int, default=20, help="结束排名（默认：20）")
    parser.add_argument("--all", action="store_true", help="显示所有书籍")
    
    args = parser.parse_args()
    view_top250(start=args.start, end=args.end, show_all=args.all)
