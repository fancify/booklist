"""豆瓣爬虫"""
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper


class DoubanScraper(BaseScraper):
    """豆瓣图书爬虫"""

    BASE_URL = "https://book.douban.com"

    async def scrape_booklist(self, url: str) -> Dict[str, Any]:
        """爬取豆瓣书单页面"""
        html = await self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        # 获取书单名称
        title_elem = soup.select_one("h1")
        name = title_elem.get_text(strip=True) if title_elem else "未知书单"

        # 解析书籍列表
        books = self._parse_book_list(soup)

        return {
            "name": name,
            "source_url": url,
            "books": books,
        }

    async def scrape_top250(self) -> Dict[str, Any]:
        """爬取豆瓣图书 Top 250"""
        all_books = []
        base_url = f"{self.BASE_URL}/top250"

        # Top 250 共 10 页，每页 25 本
        for page in range(10):
            start = page * 25
            url = f"{base_url}?start={start}"
            print(f"正在爬取第 {page + 1}/10 页: {url}")

            html = await self.fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            books = self._parse_top250_page(soup, start)
            all_books.extend(books)

            print(f"  获取 {len(books)} 本书")

        return {
            "name": "豆瓣图书 Top 250",
            "source_url": base_url,
            "books": all_books,
        }

    def _parse_top250_page(self, soup: BeautifulSoup, start: int) -> List[Dict[str, Any]]:
        """解析 Top 250 页面"""
        books = []
        items = soup.select("tr.item")

        for idx, item in enumerate(items):
            try:
                book = self._parse_top250_item(item)
                if book:
                    book["rank"] = start + idx + 1
                    books.append(book)
            except Exception as e:
                print(f"  解析书籍失败: {e}")
                continue

        return books

    def _parse_top250_item(self, item) -> Optional[Dict[str, Any]]:
        """解析 Top 250 单个书籍条目"""
        # 书名和链接
        title_elem = item.select_one("div.pl2 a")
        if not title_elem:
            return None

        title = title_elem.get("title", "").strip()
        if not title:
            title = title_elem.get_text(strip=True)

        book_url = title_elem.get("href", "")
        douban_id = self._extract_douban_id(book_url)

        # 作者/出版信息
        info_elem = item.select_one("p.pl")
        author = ""
        publisher = ""
        pub_year = ""
        if info_elem:
            info_text = info_elem.get_text(strip=True)
            # 格式: 作者 / 出版社 / 出版年 / 价格
            parts = [p.strip() for p in info_text.split("/")]
            if len(parts) >= 1:
                author = parts[0]
            if len(parts) >= 2:
                publisher = parts[1]
            if len(parts) >= 3:
                pub_year = parts[2]

        # 评分
        rating_elem = item.select_one("span.rating_nums")
        rating = rating_elem.get_text(strip=True) if rating_elem else ""

        # 封面图
        img_elem = item.select_one("img")
        cover_url = img_elem.get("src", "") if img_elem else ""

        # 简介
        quote_elem = item.select_one("span.inq")
        quote = quote_elem.get_text(strip=True) if quote_elem else ""

        return {
            "title": title,
            "author": author,
            "publisher": publisher,
            "pub_year": pub_year,
            "rating": rating,
            "cover_url": cover_url,
            "douban_id": douban_id,
            "douban_url": book_url,
            "quote": quote,
        }

    def _parse_book_list(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """解析普通书单页面的书籍列表"""
        books = []
        # 豆瓣书单页面的书籍列表
        items = soup.select("div.subject-item") or soup.select("li.subject-item")

        for idx, item in enumerate(items):
            try:
                book = self._parse_book_item(item)
                if book:
                    book["rank"] = idx + 1
                    books.append(book)
            except Exception as e:
                print(f"  解析书籍失败: {e}")
                continue

        return books

    def _parse_book_item(self, item) -> Optional[Dict[str, Any]]:
        """解析普通书单中的单个书籍"""
        # 书名
        title_elem = item.select_one("h2 a") or item.select_one("a.title")
        if not title_elem:
            return None

        title = title_elem.get("title", "") or title_elem.get_text(strip=True)
        book_url = title_elem.get("href", "")
        douban_id = self._extract_douban_id(book_url)

        # 作者信息
        info_elem = item.select_one("div.pub")
        author = ""
        if info_elem:
            info_text = info_elem.get_text(strip=True)
            parts = info_text.split("/")
            if parts:
                author = parts[0].strip()

        # 封面
        img_elem = item.select_one("img")
        cover_url = img_elem.get("src", "") if img_elem else ""

        # 评分
        rating_elem = item.select_one("span.rating_nums")
        rating = rating_elem.get_text(strip=True) if rating_elem else ""

        return {
            "title": title,
            "author": author,
            "cover_url": cover_url,
            "douban_id": douban_id,
            "douban_url": book_url,
            "rating": rating,
        }

    def _extract_douban_id(self, url: str) -> str:
        """从豆瓣URL提取书籍ID"""
        match = re.search(r"/subject/(\d+)", url)
        return match.group(1) if match else ""
