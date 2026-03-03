#!/usr/bin/env python3
"""
Unified academic paper search CLI tool across arXiv, Semantic Scholar, and DBLP.
"""

import argparse
import json
import sys
import os
import time
import difflib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlencode
import logging

import requests
import arxiv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """Data class representing an academic paper."""
    title: str
    authors: List[str]
    year: int
    venue: str
    abstract: str
    url: str
    doi: Optional[str]
    citation_count: int
    source: str  # arxiv, s2, or dblp


class ArxivSearch:
    """Search papers on arXiv."""

    @staticmethod
    def parse_date_to_arxiv(date_str: Optional[str]) -> Optional[str]:
        """
        Convert YYYY-MM format to arXiv date format (YYYYMM).
        Returns None if parsing fails.
        """
        if not date_str:
            return None
        try:
            parts = date_str.split('-')
            if len(parts) != 2:
                return None
            year, month = parts
            return f"{year}{month}"
        except Exception:
            return None

    @staticmethod
    def search(
        query: str,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        max_results: int = 20
    ) -> List[Paper]:
        """
        Search arXiv and return list of Paper objects.
        """
        papers = []
        try:
            # Build arXiv query with date range
            arxiv_query = query
            if date_start:
                arxiv_start = ArxivSearch.parse_date_to_arxiv(date_start)
                if arxiv_start:
                    arxiv_query += f" AND submittedDate:[{arxiv_start}010000 TO 99991231235959]"

            if date_end:
                arxiv_end = ArxivSearch.parse_date_to_arxiv(date_end)
                if arxiv_end:
                    # If date_end is provided without date_start, constrain from beginning
                    if not date_start:
                        arxiv_query += f" AND submittedDate:[0000010100000 TO {arxiv_end}235959]"

            client = arxiv.Client()
            search = arxiv.Search(
                query=arxiv_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )

            for entry in client.results(search):
                authors = [author.name for author in entry.authors]
                year = entry.published.year

                # Extract DOI if available
                doi = None
                if entry.doi:
                    doi = entry.doi

                paper = Paper(
                    title=entry.title,
                    authors=authors,
                    year=year,
                    venue="arXiv",
                    abstract=entry.summary,
                    url=entry.entry_id,
                    doi=doi,
                    citation_count=0,
                    source="arxiv"
                )
                papers.append(paper)

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")

        return papers


class SemanticScholarSearch:
    """Search papers on Semantic Scholar."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RATE_LIMIT_DELAY = 0.06  # 100 req/5min = ~0.06s between requests
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1.0
    MAX_BACKOFF = 30.0

    def __init__(self):
        self.api_key = os.environ.get("S2_API_KEY")
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Return request headers with API key if available."""
        headers = {"User-Agent": "PaperSearchTool/1.0"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _request_with_backoff(
        self, method: str, url: str, **kwargs
    ) -> Optional[requests.Response]:
        """
        Make HTTP request with exponential backoff.
        Returns None if all retries fail.
        """
        backoff = self.INITIAL_BACKOFF
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 429:
                    # Rate limit hit
                    if attempt < self.MAX_RETRIES - 1:
                        wait_time = min(backoff, self.MAX_BACKOFF)
                        logger.warning(
                            f"Rate limited. Waiting {wait_time}s before retry..."
                        )
                        time.sleep(wait_time)
                        backoff *= 2
                        continue

                if response.status_code >= 400:
                    last_error = f"HTTP {response.status_code}"
                    if attempt < self.MAX_RETRIES - 1:
                        wait_time = min(backoff, self.MAX_BACKOFF)
                        time.sleep(wait_time)
                        backoff *= 2
                        continue
                    return None

                return response

            except requests.RequestException as e:
                last_error = str(e)
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = min(backoff, self.MAX_BACKOFF)
                    time.sleep(wait_time)
                    backoff *= 2
                    continue
                return None

        if last_error:
            logger.error(f"Request failed after {self.MAX_RETRIES} retries: {last_error}")
        return None

    def search(
        self,
        query: str,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        max_results: int = 20
    ) -> List[Paper]:
        """
        Search Semantic Scholar and return list of Paper objects.
        """
        papers = []
        try:
            url = f"{self.BASE_URL}/paper/search"

            # Parse dates
            year_min = None
            year_max = None

            if date_start:
                try:
                    year_min = int(date_start.split('-')[0])
                except (ValueError, IndexError):
                    pass

            if date_end:
                try:
                    year_max = int(date_end.split('-')[0])
                except (ValueError, IndexError):
                    pass

            params = {
                "query": query,
                "limit": max_results,
                "fields": "title,authors,year,venue,abstract,externalIds,citationCount,url"
            }

            if year_min:
                params["yearMin"] = year_min
            if year_max:
                params["yearMax"] = year_max

            response = self._request_with_backoff(
                "GET",
                url,
                params=params,
                headers=self._get_headers()
            )

            if not response:
                logger.error("Failed to search Semantic Scholar")
                return papers

            data = response.json()

            for item in data.get("data", []):
                authors = [
                    author.get("name", "")
                    for author in item.get("authors", [])
                ]

                year = item.get("year", 0)
                if year:
                    year = int(year)

                # Extract DOI if available
                doi = None
                external_ids = item.get("externalIds", {})
                if external_ids:
                    doi = external_ids.get("DOI")

                paper = Paper(
                    title=item.get("title", ""),
                    authors=authors,
                    year=year,
                    venue=item.get("venue", ""),
                    abstract=item.get("abstract", ""),
                    url=item.get("url", ""),
                    doi=doi,
                    citation_count=item.get("citationCount", 0) or 0,
                    source="s2"
                )
                papers.append(paper)

        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")

        return papers

    def get_citations(
        self, paper_id: str, limit: int = 20
    ) -> List[Paper]:
        """
        Get papers that cite a given paper (citations endpoint).
        """
        papers = []
        try:
            url = f"{self.BASE_URL}/paper/{paper_id}/citations"
            params = {
                "limit": limit,
                "fields": "paperId,title,authors,year,venue,abstract,externalIds,citationCount,url"
            }

            response = self._request_with_backoff(
                "GET",
                url,
                params=params,
                headers=self._get_headers()
            )

            if not response:
                logger.error(f"Failed to fetch citations for paper {paper_id}")
                return papers

            data = response.json()

            for item in data.get("data", []):
                citation_entry = item.get("citingPaper", {})

                authors = [
                    author.get("name", "")
                    for author in citation_entry.get("authors", [])
                ]

                year = citation_entry.get("year", 0)
                if year:
                    year = int(year)

                doi = None
                external_ids = citation_entry.get("externalIds", {})
                if external_ids:
                    doi = external_ids.get("DOI")

                paper = Paper(
                    title=citation_entry.get("title", ""),
                    authors=authors,
                    year=year,
                    venue=citation_entry.get("venue", ""),
                    abstract=citation_entry.get("abstract", ""),
                    url=citation_entry.get("url", ""),
                    doi=doi,
                    citation_count=citation_entry.get("citationCount", 0) or 0,
                    source="s2"
                )
                papers.append(paper)

        except Exception as e:
            logger.error(f"Error fetching citations: {e}")

        return papers

    def get_references(
        self, paper_id: str, limit: int = 20
    ) -> List[Paper]:
        """
        Get papers cited by a given paper (references endpoint).
        """
        papers = []
        try:
            url = f"{self.BASE_URL}/paper/{paper_id}/references"
            params = {
                "limit": limit,
                "fields": "paperId,title,authors,year,venue,abstract,externalIds,citationCount,url"
            }

            response = self._request_with_backoff(
                "GET",
                url,
                params=params,
                headers=self._get_headers()
            )

            if not response:
                logger.error(f"Failed to fetch references for paper {paper_id}")
                return papers

            data = response.json()

            for item in data.get("data", []):
                reference_entry = item.get("citedPaper", {})

                authors = [
                    author.get("name", "")
                    for author in reference_entry.get("authors", [])
                ]

                year = reference_entry.get("year", 0)
                if year:
                    year = int(year)

                doi = None
                external_ids = reference_entry.get("externalIds", {})
                if external_ids:
                    doi = external_ids.get("DOI")

                paper = Paper(
                    title=reference_entry.get("title", ""),
                    authors=authors,
                    year=year,
                    venue=reference_entry.get("venue", ""),
                    abstract=reference_entry.get("abstract", ""),
                    url=reference_entry.get("url", ""),
                    doi=doi,
                    citation_count=reference_entry.get("citationCount", 0) or 0,
                    source="s2"
                )
                papers.append(paper)

        except Exception as e:
            logger.error(f"Error fetching references: {e}")

        return papers


class DBLPSearch:
    """Search papers on DBLP."""

    BASE_URL = "https://dblp.org/search/publ/api"

    @staticmethod
    def search(
        query: str,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        max_results: int = 20
    ) -> List[Paper]:
        """
        Search DBLP and return list of Paper objects.
        """
        papers = []
        try:
            # Parse year ranges
            year_min = None
            year_max = None

            if date_start:
                try:
                    year_min = int(date_start.split('-')[0])
                except (ValueError, IndexError):
                    pass

            if date_end:
                try:
                    year_max = int(date_end.split('-')[0])
                except (ValueError, IndexError):
                    pass

            # Build DBLP query
            dblp_query = query
            if year_min and year_max:
                dblp_query += f" year:{year_min}-{year_max}"
            elif year_min:
                dblp_query += f" year:{year_min}-"
            elif year_max:
                dblp_query += f" year:-{year_max}"

            params = {
                "q": dblp_query,
                "format": "json",
                "h": max_results
            }

            response = requests.get(
                DBLPSearch.BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            for hit in data.get("result", {}).get("hits", {}).get("hit", []):
                info = hit.get("info", {})

                # Extract authors
                authors = []
                authors_data = info.get("authors", {}).get("author", [])
                if not isinstance(authors_data, list):
                    authors_data = [authors_data] if authors_data else []

                for author in authors_data:
                    if isinstance(author, dict):
                        authors.append(author.get("text", ""))
                    elif isinstance(author, str):
                        authors.append(author)

                year = info.get("year", 0)
                if year:
                    try:
                        year = int(year)
                    except (ValueError, TypeError):
                        year = 0

                paper = Paper(
                    title=info.get("title", ""),
                    authors=authors,
                    year=year,
                    venue=info.get("venue", ""),
                    abstract="",  # DBLP doesn't provide abstracts
                    url=info.get("url", ""),
                    doi=None,
                    citation_count=0,
                    source="dblp"
                )
                papers.append(paper)

        except Exception as e:
            logger.error(f"Error searching DBLP: {e}")

        return papers


class PaperDeduplicator:
    """Deduplicates papers across sources."""

    FUZZY_MATCH_THRESHOLD = 0.85

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title for comparison."""
        return title.lower().strip()

    @staticmethod
    def _doi_match(paper1: Paper, paper2: Paper) -> bool:
        """Check if two papers match by DOI."""
        if not paper1.doi or not paper2.doi:
            return False
        return paper1.doi.lower() == paper2.doi.lower()

    @staticmethod
    def _fuzzy_title_match(paper1: Paper, paper2: Paper) -> bool:
        """Check if two papers have similar titles."""
        title1 = PaperDeduplicator._normalize_title(paper1.title)
        title2 = PaperDeduplicator._normalize_title(paper2.title)

        ratio = difflib.SequenceMatcher(None, title1, title2).ratio()
        return ratio >= PaperDeduplicator.FUZZY_MATCH_THRESHOLD

    @staticmethod
    def _metadata_score(paper: Paper) -> int:
        """
        Calculate metadata completeness score.
        S2 > DBLP > arXiv.
        """
        base_scores = {
            "s2": 100,
            "dblp": 50,
            "arxiv": 25
        }

        score = base_scores.get(paper.source, 0)

        # Bonus for abstract
        if paper.abstract:
            score += 10

        # Bonus for citation count
        if paper.citation_count > 0:
            score += 5

        # Bonus for DOI
        if paper.doi:
            score += 5

        return score

    @staticmethod
    def deduplicate(papers: List[Paper]) -> List[Paper]:
        """
        Deduplicate papers across sources.
        Returns deduplicated list, preferring entries with more metadata.
        """
        if not papers:
            return []

        seen: Set[int] = set()
        deduplicated = []

        for i, paper1 in enumerate(papers):
            if i in seen:
                continue

            # Find all duplicates of paper1
            duplicates = [paper1]
            for j in range(i + 1, len(papers)):
                if j in seen:
                    continue

                paper2 = papers[j]

                if (PaperDeduplicator._doi_match(paper1, paper2) or
                    PaperDeduplicator._fuzzy_title_match(paper1, paper2)):
                    duplicates.append(paper2)
                    seen.add(j)

            # Keep the one with best metadata
            best = max(duplicates, key=PaperDeduplicator._metadata_score)

            # Merge metadata from duplicates
            best_paper = Paper(
                title=best.title,
                authors=best.authors,
                year=best.year,
                venue=best.venue,
                abstract=best.abstract,
                url=best.url,
                doi=best.doi,
                citation_count=max(p.citation_count for p in duplicates),
                source=best.source
            )

            deduplicated.append(best_paper)
            seen.add(i)

        return deduplicated


class PaperSorter:
    """Sorts papers by different criteria."""

    @staticmethod
    def sort(
        papers: List[Paper],
        sort_by: str = "relevance"
    ) -> List[Paper]:
        """
        Sort papers by specified criteria.

        Args:
            papers: List of Paper objects
            sort_by: One of 'relevance', 'date', 'citations'

        Returns:
            Sorted list of papers
        """
        if sort_by == "date":
            return sorted(papers, key=lambda p: p.year, reverse=True)
        elif sort_by == "citations":
            return sorted(papers, key=lambda p: p.citation_count, reverse=True)
        else:  # relevance (default order)
            return papers


class PaperSearchCLI:
    """Main CLI interface."""

    def __init__(self):
        self.arxiv_search = ArxivSearch()
        self.s2_search = SemanticScholarSearch()
        self.dblp_search = DBLPSearch()

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="Unified academic paper search across arXiv, Semantic Scholar, and DBLP"
        )

        parser.add_argument(
            "--query",
            required=False,
            help="Search query string"
        )

        parser.add_argument(
            "--sources",
            default="arxiv,s2,dblp",
            help="Comma-separated sources: arxiv,s2,dblp (default: arxiv,s2,dblp)"
        )

        parser.add_argument(
            "--date-start",
            help="Start date in YYYY-MM format (default: 1 year ago)"
        )

        parser.add_argument(
            "--date-end",
            help="End date in YYYY-MM format (default: now)"
        )

        parser.add_argument(
            "--max-results",
            type=int,
            default=20,
            help="Max papers per source (default: 20)"
        )

        parser.add_argument(
            "--venues",
            help="Filter by venues, comma-separated"
        )

        parser.add_argument(
            "--output",
            choices=["json", "markdown"],
            default="json",
            help="Output format: json or markdown (default: json)"
        )

        parser.add_argument(
            "--sort",
            choices=["relevance", "date", "citations"],
            default="relevance",
            help="Sort by: relevance, date, or citations (default: relevance)"
        )

        parser.add_argument(
            "--paper-id",
            help="Semantic Scholar paper ID for citation graph traversal"
        )

        parser.add_argument(
            "--citing",
            action="store_true",
            help="Return papers that cite the specified paper"
        )

        parser.add_argument(
            "--cited-by",
            action="store_true",
            help="Return papers cited by the specified paper"
        )

        return parser.parse_args()

    def _default_date_start(self) -> str:
        """Get default start date (1 year ago)."""
        one_year_ago = datetime.now() - timedelta(days=365)
        return one_year_ago.strftime("%Y-%m")

    def filter_by_venues(
        self, papers: List[Paper], venues_str: str
    ) -> List[Paper]:
        """Filter papers by venue."""
        if not venues_str:
            return papers

        venues = {v.strip().lower() for v in venues_str.split(",")}
        return [
            p for p in papers
            if p.venue.lower() in venues
        ]

    def search(self, args: argparse.Namespace) -> List[Paper]:
        """Execute search across specified sources."""
        all_papers = []

        # Determine if this is a citation graph traversal
        if args.paper_id:
            if args.citing:
                logger.info(f"Fetching papers citing {args.paper_id}...")
                papers = self.s2_search.get_citations(
                    args.paper_id,
                    limit=args.max_results
                )
                all_papers.extend(papers)

            if args.cited_by:
                logger.info(f"Fetching papers cited by {args.paper_id}...")
                papers = self.s2_search.get_references(
                    args.paper_id,
                    limit=args.max_results
                )
                all_papers.extend(papers)

            # If neither flag is set, get both by default
            if not args.citing and not args.cited_by:
                logger.info(f"Fetching papers citing {args.paper_id}...")
                citing_papers = self.s2_search.get_citations(
                    args.paper_id,
                    limit=args.max_results
                )
                all_papers.extend(citing_papers)

                logger.info(f"Fetching papers cited by {args.paper_id}...")
                cited_papers = self.s2_search.get_references(
                    args.paper_id,
                    limit=args.max_results
                )
                all_papers.extend(cited_papers)

        else:
            # Regular keyword search
            if not args.query:
                logger.error("--query is required for keyword search")
                return []

            # Set default date_start if not provided
            date_start = args.date_start or self._default_date_start()
            date_end = args.date_end

            sources = {s.strip().lower() for s in args.sources.split(",")}

            if "arxiv" in sources:
                logger.info("Searching arXiv...")
                papers = self.arxiv_search.search(
                    args.query,
                    date_start=date_start,
                    date_end=date_end,
                    max_results=args.max_results
                )
                all_papers.extend(papers)

            if "s2" in sources:
                logger.info("Searching Semantic Scholar...")
                papers = self.s2_search.search(
                    args.query,
                    date_start=date_start,
                    date_end=date_end,
                    max_results=args.max_results
                )
                all_papers.extend(papers)

            if "dblp" in sources:
                logger.info("Searching DBLP...")
                papers = self.dblp_search.search(
                    args.query,
                    date_start=date_start,
                    date_end=date_end,
                    max_results=args.max_results
                )
                all_papers.extend(papers)

        # Deduplicate
        logger.info(f"Deduplicating {len(all_papers)} papers...")
        all_papers = PaperDeduplicator.deduplicate(all_papers)

        # Filter by venues if specified
        if args.venues:
            all_papers = self.filter_by_venues(all_papers, args.venues)

        # Sort
        all_papers = PaperSorter.sort(all_papers, sort_by=args.sort)

        return all_papers

    def format_json(self, papers: List[Paper]) -> str:
        """Format papers as JSON."""
        papers_dicts = [asdict(p) for p in papers]
        return json.dumps(papers_dicts, indent=2, ensure_ascii=False)

    def format_markdown(self, papers: List[Paper]) -> str:
        """Format papers as markdown table."""
        if not papers:
            return "No papers found."

        lines = [
            "| Title | Authors | Year | Venue | Citation Count | Source |",
            "|-------|---------|------|-------|----------------|--------|"
        ]

        for paper in papers:
            authors_str = "; ".join(paper.authors[:3])  # First 3 authors
            if len(paper.authors) > 3:
                authors_str += f" et al. ({len(paper.authors)})"

            title_str = paper.title[:60] + "..." if len(paper.title) > 60 else paper.title

            lines.append(
                f"| {title_str} | {authors_str} | {paper.year} | {paper.venue} | {paper.citation_count} | {paper.source} |"
            )

        return "\n".join(lines)

    def run(self) -> int:
        """Main entry point."""
        try:
            args = self.parse_args()

            papers = self.search(args)

            if args.output == "json":
                output = self.format_json(papers)
            else:  # markdown
                output = self.format_markdown(papers)

            print(output)

            return 0

        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Entry point."""
    cli = PaperSearchCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
