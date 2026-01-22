"""爬虫基类"""
import httpx
import asyncio
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseScraper(ABC):
    """爬虫基类"""

    # 默认请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, delay: float = 1.0):
        """
        初始化爬虫

        Args:
            delay: 请求间隔（秒），避免被封
        """
        self.delay = delay
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.DEFAULT_HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def fetch(self, url: str) -> str:
        """获取页面内容"""
        # 随机延迟，避免请求过于规律
        await asyncio.sleep(self.delay + random.uniform(0, 0.5))
        response = await self.client.get(url)
        response.raise_for_status()
        return response.text

    @abstractmethod
    async def scrape_booklist(self, url: str) -> Dict[str, Any]:
        """
        爬取书单

        Returns:
            {
                "name": "书单名称",
                "source_url": "来源URL",
                "books": [
                    {"title": "书名", "author": "作者", "isbn": "ISBN", ...},
                    ...
                ]
            }
        """
        pass
