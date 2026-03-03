#!/usr/bin/env python3
"""
BibTeX utilities for fetching, merging, and validating BibTeX entries.

Never fabricates citations. Supports fetching from Semantic Scholar, DBLP, and arXiv.
"""

import argparse
import json
import os
import sys
import time
import re
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

try:
    from pybtex.database import parse_file, BibliographyData, Entry
    from pybtex.latexenc import latex_to_text
except ImportError:
    print("Error: pybtex is required. Install with: pip install pybtex", file=sys.stderr)
    sys.exit(1)


@dataclass
class ValidationIssue:
    """Represents a validation issue in a BibTeX entry."""
    key: str
    issue: str
    severity: str  # "error" or "warning"


class BibtexFetcher:
    """Fetches BibTeX entries from various sources."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("S2_API_KEY")
        self.base_delay = 1.0
        self.max_delay = 30.0
        self.max_retries = 3

    def _request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with exponential backoff."""
        if headers is None:
            headers = {}

        headers["User-Agent"] = "bibtex-utils/1.0"
        if self.api_key:
            headers["x-api-key"] = self.api_key

        delay = self.base_delay
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, self.max_delay)
                else:
                    print(f"Error: Failed to fetch {url} after {self.max_retries} retries", file=sys.stderr)
                    return None
            except Exception as e:
                print(f"Error: Request failed: {e}", file=sys.stderr)
                return None

        return None

    def _fetch_s2_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Fetch paper metadata from Semantic Scholar by DOI."""
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
        params = {
            "fields": "externalIds,title,authors,year,venue,publicationDate,abstract"
        }
        url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
        return self._request(url_with_params)

    def _fetch_s2_bibtex(self, s2_id: str) -> Optional[str]:
        """Fetch BibTeX entry from Semantic Scholar paper."""
        url = f"https://api.semanticscholar.org/graph/v1/paper/{s2_id}/citation-styles/bibtex"
        response = self._request(url)
        if response and isinstance(response, dict) and "bibtex" in response:
            return response["bibtex"]
        return None

    def _search_s2_by_title(self, title: str) -> Optional[str]:
        """Search Semantic Scholar by title and return S2 ID of top result."""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {"query": title, "limit": 1}
        url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
        response = self._request(url_with_params)

        if response and "results" in response and len(response["results"]) > 0:
            return response["results"][0].get("paperId")
        return None

    def _search_dblp_by_title(self, title: str) -> Optional[str]:
        """Search DBLP by title and return BibTeX URL."""
        url = "https://dblp.org/search/publ/api"
        params = {"q": title, "format": "json"}
        url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
        response = self._request(url_with_params)

        if response and "result" in response and "hits" in response["result"]:
            hits = response["result"]["hits"]
            if "hit" in hits and len(hits["hit"]) > 0:
                # DBLP returns partial matches; construct BibTeX URL
                dblp_key = hits["hit"][0].get("info", {}).get("key")
                if dblp_key:
                    return f"https://dblp.org/rec/{dblp_key}.bib"
        return None

    def _fetch_dblp_bibtex(self, bibtex_url: str) -> Optional[str]:
        """Fetch BibTeX content from DBLP URL."""
        try:
            req = urllib.request.Request(bibtex_url)
            req.add_header("User-Agent", "bibtex-utils/1.0")
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error: Failed to fetch DBLP BibTeX: {e}", file=sys.stderr)
            return None

    def _search_arxiv_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search arXiv by title and return metadata of top result."""
        # Construct arXiv API URL
        query = urllib.parse.quote(f"title:{title}")
        url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=1"

        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "bibtex-utils/1.0")
            with urllib.request.urlopen(req, timeout=10) as response:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.read())

                # Parse Atom response
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", ns)
                if entries:
                    entry = entries[0]
                    arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
                    title_elem = entry.find("atom:title", ns)
                    authors_elems = entry.findall("atom:author", ns)
                    published = entry.find("atom:published", ns).text

                    authors = []
                    for auth_elem in authors_elems:
                        name_elem = auth_elem.find("atom:name", ns)
                        if name_elem is not None:
                            authors.append(name_elem.text)

                    return {
                        "arxiv_id": arxiv_id,
                        "title": title_elem.text if title_elem is not None else "",
                        "authors": authors,
                        "published": published,
                    }
        except Exception as e:
            print(f"Error: Failed to fetch arXiv metadata: {e}", file=sys.stderr)
            return None

        return None

    def _extract_first_author_year(self, bibtex_str: str) -> Tuple[Optional[str], Optional[int]]:
        """Extract first author last name and year from BibTeX entry."""
        try:
            # Parse BibTeX
            from io import StringIO
            from pybtex.database import parse_string

            bib_data = parse_string(bibtex_str, bib_format='bibtex')
            if not bib_data.entries:
                return None, None

            entry = list(bib_data.entries.values())[0]

            # Extract first author
            if "author" in entry.persons:
                authors = entry.persons["author"]
                if authors:
                    first_author = authors[0]
                    last_name = str(first_author.prelast_names() + first_author.last_names())
                    last_name = last_name.replace(" ", "").replace("-", "")
            else:
                return None, None

            # Extract year
            year = None
            if "year" in entry.fields:
                try:
                    year = int(entry.fields["year"])
                except (ValueError, TypeError):
                    return first_author, None

            return first_author, year
        except Exception as e:
            print(f"Error: Failed to parse BibTeX for citation key: {e}", file=sys.stderr)
            return None, None

    def _generate_citation_key(self, bibtex_str: str) -> Optional[str]:
        """Generate citation key in format: FirstAuthorLastNameYear."""
        first_author, year = self._extract_first_author_year(bibtex_str)

        if not first_author or not year:
            return None

        # Clean up last name (remove spaces, dashes)
        last_name = re.sub(r'[^\w]', '', str(first_author)).strip()
        if not last_name:
            return None

        return f"{last_name}{year}"

    def _rewrite_citation_key(self, bibtex_str: str) -> str:
        """Rewrite the citation key in a BibTeX entry."""
        new_key = self._generate_citation_key(bibtex_str)
        if not new_key:
            return bibtex_str

        # Find and replace the citation key
        match = re.match(r'(@\w+\{)([^,]+)(,.*)$', bibtex_str, re.DOTALL)
        if match:
            return match.group(1) + new_key + match.group(3)

        return bibtex_str

    def fetch(self, doi: Optional[str] = None, title: Optional[str] = None,
              source: str = "s2") -> Optional[str]:
        """
        Fetch BibTeX entry. Supports DOI or title.
        Falls back through: S2 → DBLP → arXiv.
        """
        bibtex = None

        if doi:
            print(f"Fetching by DOI: {doi}", file=sys.stderr)
            metadata = self._fetch_s2_by_doi(doi)
            if metadata and "paperId" in metadata:
                s2_id = metadata["paperId"]
                bibtex = self._fetch_s2_bibtex(s2_id)
                if bibtex:
                    return self._rewrite_citation_key(bibtex)

        if title:
            print(f"Fetching by title: {title}", file=sys.stderr)

            # Try Semantic Scholar
            if source in ["s2", None]:
                s2_id = self._search_s2_by_title(title)
                if s2_id:
                    bibtex = self._fetch_s2_bibtex(s2_id)
                    if bibtex:
                        return self._rewrite_citation_key(bibtex)

            # Try DBLP
            if source in ["dblp", None]:
                bibtex_url = self._search_dblp_by_title(title)
                if bibtex_url:
                    bibtex = self._fetch_dblp_bibtex(bibtex_url)
                    if bibtex:
                        return self._rewrite_citation_key(bibtex)

            # Try arXiv
            if source in ["arxiv", None]:
                metadata = self._search_arxiv_by_title(title)
                if metadata:
                    bibtex = self._arxiv_metadata_to_bibtex(metadata)
                    if bibtex:
                        return self._rewrite_citation_key(bibtex)

        return None

    def _arxiv_metadata_to_bibtex(self, metadata: Dict[str, Any]) -> str:
        """Convert arXiv metadata to BibTeX entry."""
        authors = " and ".join(metadata.get("authors", []))
        year = metadata.get("published", "")[:4] if metadata.get("published") else ""
        arxiv_id = metadata.get("arxiv_id", "")
        title = metadata.get("title", "")

        # Clean title
        title = title.replace("\n", " ").strip()

        bibtex = f"""@article{{{arxiv_id},
  title={{{title}}},
  author={{{authors}}},
  year={{{year}}},
  arxivId={{{arxiv_id}}},
  eprint={{{arxiv_id}}},
  archivePrefix={{arXiv}}
}}"""
        return bibtex


class BibtexMerger:
    """Merges multiple BibTeX files with deduplication."""

    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalize title for comparison."""
        return re.sub(r'\s+', ' ', title).lower().strip()

    @staticmethod
    def merge_files(file_paths: List[str]) -> BibliographyData:
        """Merge multiple BibTeX files with deduplication."""
        merged = BibliographyData()
        doi_map = {}  # Track DOIs to detect duplicates
        title_map = {}  # Track normalized titles

        for file_path in file_paths:
            try:
                bib_data = parse_file(file_path)

                for key, entry in bib_data.entries.items():
                    doi = entry.fields.get("doi", "").lower().strip() if "doi" in entry.fields else None
                    title_normalized = BibtexMerger.normalize_title(
                        entry.fields.get("title", "")
                    ) if "title" in entry.fields else None

                    # Check for duplicate by DOI
                    if doi and doi in doi_map:
                        existing_key = doi_map[doi]
                        existing_entry = merged.entries[existing_key]
                        # Keep entry with more fields
                        if len(entry.fields) > len(existing_entry.fields):
                            merged.entries[existing_key] = entry
                        continue

                    # Check for duplicate by normalized title
                    if title_normalized and title_normalized in title_map:
                        existing_key = title_map[title_normalized]
                        existing_entry = merged.entries[existing_key]
                        # Keep entry with more fields
                        if len(entry.fields) > len(existing_entry.fields):
                            merged.entries[existing_key] = entry
                        continue

                    # Add new entry
                    new_key = key
                    counter = 1
                    while new_key in merged.entries:
                        new_key = f"{key}_{counter}"
                        counter += 1

                    merged.entries[new_key] = entry

                    if doi:
                        doi_map[doi] = new_key
                    if title_normalized:
                        title_map[title_normalized] = new_key

            except Exception as e:
                print(f"Error: Failed to parse {file_path}: {e}", file=sys.stderr)
                continue

        return merged


class BibtexValidator:
    """Validates BibTeX files."""

    REQUIRED_FIELDS = {
        "article": ["title", "author", "year"],
        "inproceedings": ["title", "author", "year"],
        "conference": ["title", "author", "year"],
        "book": ["title", "author", "year"],
        "incollection": ["title", "author", "year"],
        "inbook": ["title", "author", "year"],
    }

    @staticmethod
    def validate_file(file_path: str) -> List[ValidationIssue]:
        """Validate a BibTeX file."""
        issues: List[ValidationIssue] = []

        try:
            bib_data = parse_file(file_path)
        except Exception as e:
            return [ValidationIssue(
                key="<file>",
                issue=f"Failed to parse file: {e}",
                severity="error"
            )]

        seen_keys = set()

        for key, entry in bib_data.entries.items():
            # Check for duplicate keys
            if key in seen_keys:
                issues.append(ValidationIssue(
                    key=key,
                    issue="Duplicate citation key",
                    severity="error"
                ))
            seen_keys.add(key)

            # Check required fields based on entry type
            entry_type = entry.type.lower()
            required = BibtexValidator.REQUIRED_FIELDS.get(entry_type, ["title", "author", "year"])

            for field in required:
                if field not in entry.fields:
                    issues.append(ValidationIssue(
                        key=key,
                        issue=f"Missing required field: {field}",
                        severity="error"
                    ))
                elif not entry.fields[field].strip():
                    issues.append(ValidationIssue(
                        key=key,
                        issue=f"Empty field: {field}",
                        severity="error"
                    ))

            # Check for malformed entries
            if not entry.fields.get("title", "").strip():
                issues.append(ValidationIssue(
                    key=key,
                    issue="Title is empty or missing",
                    severity="error"
                ))

            if not entry.fields.get("author", "").strip():
                issues.append(ValidationIssue(
                    key=key,
                    issue="Author is empty or missing",
                    severity="error"
                ))

            # Try to parse year field
            if "year" in entry.fields:
                year_str = entry.fields["year"].strip()
                if year_str:
                    try:
                        year_int = int(year_str)
                        if year_int < 1000 or year_int > 2100:
                            issues.append(ValidationIssue(
                                key=key,
                                issue=f"Year out of reasonable range: {year_int}",
                                severity="warning"
                            ))
                    except ValueError:
                        issues.append(ValidationIssue(
                            key=key,
                            issue=f"Invalid year format: {year_str}",
                            severity="warning"
                        ))

        return issues


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BibTeX utilities for fetching, merging, and validating citations",
        prog="bibtex_utils"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch BibTeX entry by DOI or title")
    fetch_parser.add_argument("--doi", type=str, help="DOI of the paper")
    fetch_parser.add_argument("--title", type=str, help="Title of the paper")
    fetch_parser.add_argument(
        "--source",
        type=str,
        choices=["s2", "dblp", "arxiv"],
        default="s2",
        help="Preferred source for fetching (default: s2)"
    )
    fetch_parser.add_argument("--output", type=str, help="Output file path")

    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge multiple BibTeX files")
    merge_parser.add_argument(
        "--files",
        type=str,
        required=True,
        help="Comma-separated list of BibTeX files to merge"
    )
    merge_parser.add_argument("--output", type=str, help="Output file path")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate BibTeX file")
    validate_parser.add_argument("--file", type=str, required=True, help="BibTeX file to validate")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Fetch command
    if args.command == "fetch":
        if not args.doi and not args.title:
            print("Error: Either --doi or --title is required", file=sys.stderr)
            sys.exit(1)

        fetcher = BibtexFetcher()
        bibtex = fetcher.fetch(doi=args.doi, title=args.title, source=args.source)

        if not bibtex:
            print("Error: Failed to fetch BibTeX entry", file=sys.stderr)
            sys.exit(1)

        if args.output:
            try:
                Path(args.output).write_text(bibtex)
                print(f"BibTeX entry written to {args.output}", file=sys.stderr)
            except Exception as e:
                print(f"Error: Failed to write output file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(bibtex)

    # Merge command
    elif args.command == "merge":
        file_list = [f.strip() for f in args.files.split(",")]

        # Validate that all files exist
        for file_path in file_list:
            if not Path(file_path).exists():
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                sys.exit(1)

        try:
            merged_data = BibtexMerger.merge_files(file_list)

            if args.output:
                try:
                    merged_data.to_file(args.output)
                    print(f"Merged BibTeX written to {args.output}", file=sys.stderr)
                except Exception as e:
                    print(f"Error: Failed to write output file: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Output to stdout
                from pybtex.latexenc import latex_to_text
                output = []
                for key, entry in merged_data.entries.items():
                    output.append(entry.to_string('bibtex'))
                print("\n".join(output))

        except Exception as e:
            print(f"Error: Merge failed: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate command
    elif args.command == "validate":
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        try:
            issues = BibtexValidator.validate_file(args.file)

            # Output as JSON
            output = [
                {
                    "key": issue.key,
                    "issue": issue.issue,
                    "severity": issue.severity
                }
                for issue in issues
            ]
            print(json.dumps(output, indent=2))

            # Exit with error code if there are critical issues
            if any(issue.severity == "error" for issue in issues):
                sys.exit(1)

        except Exception as e:
            print(f"Error: Validation failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
