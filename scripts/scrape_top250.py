#!/usr/bin/env python3
"""爬取豆瓣 Top 250 的脚本"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.services.scraper_service import scrape_and_save_top250


async def main():
    print("=" * 50)
    print("豆瓣图书 Top 250 爬虫")
    print("=" * 50)

    # 初始化数据库
    init_db()
    db = SessionLocal()

    try:
        result = await scrape_and_save_top250(db, booklist_name="豆瓣")

        print("\n" + "=" * 50)
        print("爬取完成！")
        print("=" * 50)
        print(f"原始书单: {result['raw_booklist_name']} (ID: {result['raw_booklist_id']})")
        print(f"归属书单: {result['booklist_name']} (ID: {result['booklist_id']})")
        print(f"统计:")
        print(f"  - 总计: {result['stats']['total']} 本")
        print(f"  - 新增: {result['stats']['new_books']} 本")
        print(f"  - 已存在: {result['stats']['existing_books']} 本")

    except Exception as e:
        print(f"\n爬取失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
