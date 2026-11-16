"""Research provider abstraction with a public encyclopedia implementation."""
from __future__ import annotations
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

class ResearchProvider:
    def search(self, query: str, limit: int = 5) -> list[dict[str, str]]:
        raise NotImplementedError

class WikipediaProvider(ResearchProvider):
    def __init__(self, timeout: float = 10):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> list[dict[str, str]]:
        url = "https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch=" + quote(query)
        request = Request(url, headers={"User-Agent": "ARD-Intelligence/0.1 (research client)"})
        with urlopen(request, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return [{"title": row["title"], "snippet": row["snippet"], "url": "https://en.wikipedia.org/?curid=" + str(row["pageid"])} for row in data.get("query", {}).get("search", [])[:max(1, min(limit, 10))]]
