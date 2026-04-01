"""
WebTool — Ricerca web per il ReasoningEngine.

Permette all'engine di:
- Cercare informazioni online
- Leggere pagine web
- Estrarre contenuti
- Ricerca semantica
"""

import urllib.request
import urllib.parse
import json
import re
from html.parser import HTMLParser


class SimpleHTMLParser(HTMLParser):
    """Parser HTML semplice per estrarre testo."""

    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
        self.skip_tags = {"script", "style", "head", "meta", "link"}

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data.strip())

    def get_text(self):
        return " ".join([t for t in self.text if t])


class WebTool:
    """Tool per ricerca web."""

    def __init__(self):
        self.search_history = []
        self.cache = {}

    def search(self, query: str, max_results: int = 5) -> dict:
        """
        Cerca informazioni online.

        Strategia multipla:
        1. DuckDuckGo Instant Answer API
        2. DuckDuckGo HTML search (fallback)
        """
        results = []

        try:
            # 1. DuckDuckGo Instant Answer API
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ReasoningEngine/1.0)"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            if data.get("Abstract"):
                results.append(
                    {
                        "type": "direct_answer",
                        "title": data.get("Heading", data.get("AbstractText", "")),
                        "content": data.get("Abstract", ""),
                        "source": data.get("AbstractSource", ""),
                        "url": data.get("AbstractURL", ""),
                    }
                )

            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(
                        {
                            "type": "related",
                            "title": topic.get("FirstURL", "")
                            .split("/")[-1]
                            .replace("_", " "),
                            "content": topic.get("Text", ""),
                            "url": topic.get("FirstURL", ""),
                        }
                    )

            if data.get("Answer"):
                results.insert(
                    0,
                    {
                        "type": "answer",
                        "title": "Risposta diretta",
                        "content": data.get("Answer", ""),
                        "source": data.get("AnswerType", ""),
                    },
                )

        except Exception:
            pass

        # 2. Fallback: DuckDuckGo HTML scraping
        if len(results) < 2:
            try:
                encoded_query = urllib.parse.quote(query)
                html_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

                req = urllib.request.Request(
                    html_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )

                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode("utf-8", errors="ignore")

                # Estrai risultati dal HTML
                import re

                snippets = re.findall(
                    r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL
                )
                titles = re.findall(
                    r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL
                )
                urls = re.findall(
                    r'class="result__url"[^>]*>(.*?)</a>', html, re.DOTALL
                )

                for i in range(min(max_results, len(snippets))):
                    title = (
                        re.sub(r"<[^>]+>", "", titles[i]).strip()
                        if i < len(titles)
                        else ""
                    )
                    content = re.sub(r"<[^>]+>", "", snippets[i]).strip()
                    url = (
                        re.sub(r"<[^>]+>", "", urls[i]).strip() if i < len(urls) else ""
                    )

                    if content:
                        results.append(
                            {
                                "type": "web_result",
                                "title": title,
                                "content": content,
                                "url": url,
                            }
                        )
            except Exception:
                pass

        self.search_history.append({"query": query, "results_count": len(results)})

        return {
            "success": len(results) > 0,
            "query": query,
            "results": results[:max_results],
            "count": len(results),
        }

    def search_and_summarize(self, query: str) -> dict:
        """Cerca e restituisce un riassunto dei risultati."""
        result = self.search(query, max_results=3)

        if not result["success"]:
            return {
                "success": False,
                "query": query,
                "summary": "Nessun risultato trovato.",
                "sources": [],
            }

        # Combina i contenuti
        parts = []
        sources = []
        for r in result["results"]:
            content = r.get("content", "")
            if content:
                parts.append(content)
            if r.get("url"):
                sources.append(r["url"])

        summary = " | ".join(parts[:3])
        if len(summary) > 500:
            summary = summary[:500] + "..."

        return {
            "success": True,
            "query": query,
            "summary": summary,
            "sources": sources,
            "results_count": result["count"],
        }

    def fetch_page(self, url: str, max_chars: int = 5000) -> dict:
        """
        Scarica e legge una pagina web.
        """
        try:
            # Controlla cache
            if url in self.cache:
                return self.cache[url]

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ReasoningEngine/1.0)"},
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode("utf-8", errors="ignore")

            # Estrai testo
            parser = SimpleHTMLParser()
            parser.feed(html)
            text = parser.get_text()

            # Limita lunghezza
            if len(text) > max_chars:
                text = text[:max_chars] + "..."

            result = {"success": True, "url": url, "text": text, "length": len(text)}

            # Cache
            self.cache[url] = result

            return result

        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}

    def extract_info(self, text: str, topic: str) -> dict:
        """
        Estrae informazioni rilevanti dal testo.
        """
        sentences = text.split(".")
        relevant = []

        topic_words = topic.lower().split()

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in topic_words):
                relevant.append(sentence.strip())

        return {
            "topic": topic,
            "relevant_sentences": relevant[:5],
            "count": len(relevant),
        }

    def get_stats(self) -> dict:
        """Statistiche."""
        return {"searches": len(self.search_history), "cached_pages": len(self.cache)}
