"""Web skill — fetch URLs and search the web."""
import json
import urllib.parse
import requests
from skills.base import BaseSkill


class WebSkill(BaseSkill):
    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_fetch",
                    "description": "Fetch a URL and return its text content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"},
                            "max_chars": {
                                "type": "integer",
                                "description": "Max response chars (default 6000)",
                            },
                        },
                        "required": ["url"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web using DuckDuckGo and return results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "num_results": {
                                "type": "integer",
                                "description": "Number of results (default 5)",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

    def handles(self) -> list[str]:
        return ["web_fetch", "web_search"]

    def call(self, name: str, arguments: dict) -> str:
        if name == "web_fetch":
            return self._fetch(**arguments)
        if name == "web_search":
            return self._search(**arguments)
        return f"[ERROR] Unknown web tool: {name}"

    def _fetch(self, url: str, max_chars: int = 6000) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 TermuxAgent/1.0"}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            text = resp.text
            # Strip obvious HTML tags minimally
            import re
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > max_chars:
                text = text[:max_chars] + "... [truncated]"
            return text
        except Exception as e:
            return f"[ERROR] {e}"

    def _search(self, query: str, num_results: int = 5) -> str:
        try:
            # Use DuckDuckGo instant answer API
            q = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            results = []
            if data.get("AbstractText"):
                results.append(f"Summary: {data['AbstractText']}")
            for r in data.get("RelatedTopics", [])[:num_results]:
                if isinstance(r, dict) and r.get("Text"):
                    results.append(f"- {r['Text']}")

            if not results:
                return f"No results found for: {query}"
            return "\n".join(results)
        except Exception as e:
            return f"[ERROR searching] {e}"
