"""爬虫服务 - 处理爬取和存储逻辑"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Book, RawBooklist, RawBooklistItem, Booklist
from app.scrapers.douban import DoubanScraper


async def scrape_and_save_top250(db: Session, booklist_name: str = "豆瓣") -> Dict[str, Any]:
    """
    爬取豆瓣 Top 250 并保存到数据库

    Args:
        db: 数据库 session
        booklist_name: 归属的 Booklist 名称

    Returns:
        爬取结果统计
    """
    # 1. 确保 Booklist 存在
    booklist = db.query(Booklist).filter(Booklist.name == booklist_name).first()
    if not booklist:
        booklist = Booklist(name=booklist_name, description="豆瓣图书榜单汇总")
        db.add(booklist)
        db.commit()
        db.refresh(booklist)

    # 2. 爬取数据
    async with DoubanScraper(delay=1.5) as scraper:
        result = await scraper.scrape_top250()

    # 3. 创建原始书单
    raw_booklist = RawBooklist(
        name=result["name"],
        source_url=result["source_url"],
        booklist_id=booklist.id,
    )
    db.add(raw_booklist)
    db.commit()
    db.refresh(raw_booklist)

    # 4. 保存书籍
    stats = {"total": 0, "new_books": 0, "existing_books": 0}

    for book_data in result["books"]:
        stats["total"] += 1

        # 查找或创建书籍
        book = find_or_create_book(db, book_data)
        if book.id is None:
            stats["new_books"] += 1
        else:
            stats["existing_books"] += 1

        db.add(book)
        db.commit()
        db.refresh(book)

        # 创建关联
        item = RawBooklistItem(
            raw_booklist_id=raw_booklist.id,
            book_id=book.id,
            rank=book_data.get("rank"),
        )
        db.add(item)

    db.commit()

    return {
        "raw_booklist_id": raw_booklist.id,
        "raw_booklist_name": raw_booklist.name,
        "booklist_id": booklist.id,
        "booklist_name": booklist.name,
        "stats": stats,
    }


def find_or_create_book(db: Session, book_data: Dict[str, Any]) -> Book:
    """
    查找或创建书籍（简单版本，后续会增加模糊匹配）

    优先级：
    1. 豆瓣ID匹配
    2. ISBN匹配
    3. 创建新书籍
    """
    douban_id = book_data.get("douban_id")
    isbn = book_data.get("isbn")

    # 尝试通过豆瓣ID查找
    if douban_id:
        book = db.query(Book).filter(Book.douban_id == douban_id).first()
        if book:
            return book

    # 尝试通过ISBN查找
    if isbn:
        book = db.query(Book).filter(Book.isbn == isbn).first()
        if book:
            return book

    # 创建新书籍
    book = Book(
        title=book_data.get("title", ""),
        author=book_data.get("author", ""),
        isbn=isbn,
        douban_id=douban_id,
        cover_url=book_data.get("cover_url", ""),
        description=book_data.get("quote", ""),
    )
    return book
