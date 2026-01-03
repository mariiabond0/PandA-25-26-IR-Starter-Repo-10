from __future__ import annotations
from typing import List, Dict, Any, Tuple


class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]

    @staticmethod
    def find_spans(text: str, pattern: str):
        """Return [(start, end), ...] for all (possibly overlapping) matches.
        Inputs should already be lowercased by the caller."""
        spans = []
        if not pattern:
            return spans

        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
                spans.append((i, i + len(pattern)))
        return spans

    def search_for(self: Sonnet, query: str) -> SearchResult:
        title_raw = str(self.title)
        lines_raw = self.lines

        q = query.lower()
        title_spans = self.find_spans(title_raw.lower(), q)

        line_matches = []
        for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
            spans = self.find_spans(line_raw.lower(), q)
            if spans:
                line_matches.append(LineMatch(idx, line_raw, spans))

        total = len(title_spans) + sum(len(lm.spans) for lm in line_matches)

        return SearchResult(title_raw, title_spans, line_matches, total)


class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, self.spans)


class SearchResult:
    def __init__(self, title: str, title_spans: List[Tuple[int, int]], line_matches: List[LineMatch], matches: int) -> None:
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(self.title, self.title_spans, self.line_matches, self.matches)

    @staticmethod
    def ansi_highlight(text: str, spans: List[Tuple[int, int]], highlight_mode) -> str:
        """Return text with ANSI highlight escape codes inserted."""
        if not spans:
            return text

        spans = sorted(spans)
        merged = []

        # Merge overlapping spans
        current_start, current_end = spans[0]
        for s, e in spans[1:]:
            if s <= current_end:
                current_end = max(current_end, e)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = s, e
        merged.append((current_start, current_end))

        if highlight_mode == "GREEN":
            color_code = "\033[1;92m"  # bold light-green text
        else:
            color_code = "\033[43m\033[30m"

        # Build highlighted string
        out = []
        i = 0
        for s, e in merged:
            out.append(text[i:s])
            # out.append("\033[43m\033[30m")  # yellow background, black text
            out.append(color_code)
            out.append(text[s:e])
            # ToDo 0: This stays the same. It just means "continue with default colors"
            out.append("\033[0m")           # reset
            i = e
        out.append(text[i:])
        return "".join(out)

    def print(self, idx, highlight, total_docs, highlight_mode):
        title_line = (
            # ToDo 0: You will need to pass the new setting, the highlight_mode to ansi_highlight and use it there
            self.ansi_highlight(self.title, self.title_spans, highlight_mode)
            if highlight
            else self.title
        )
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in self.line_matches:
            line_out = (
                # ToDo 0: You will need to pass the new setting, the highlight_mode to ansi_highlight and use it there
                self.ansi_highlight(lm.text, lm.spans, highlight_mode)
                if highlight
                else lm.text
            )
            print(f"  [{lm.line_no:2}] {line_out}")

    def combine_with(self: SearchResult, other: SearchResult) -> SearchResult:
        """Combine two search results."""

        combined = self.copy()  # shallow copy

        combined.matches = self.matches + other.matches
        combined.title_spans = sorted(self.title_spans + other.title_spans)

        # Merge line_matches by line number
        lines_by_no = {lm.line_no: lm.copy() for lm in self.line_matches}
        for lm in other.line_matches:
            ln = lm.line_no
            if ln in lines_by_no:
                # extend spans & keep original text
                lines_by_no[ln].spans.extend(lm.spans)
            else:
                lines_by_no[ln] = lm.copy()

        combined.line_matches = sorted(lines_by_no.values(), key=lambda lm: lm.line_no)

        return combined

# ------------------------- Search behaviour ---------------------------------


class SonnetsSearcher:
    def __init__(self, sonnets: List[Sonnet]):
        self.sonnets = sonnets

    def search(self, query: str, search_mode: str) -> List[SearchResult]:
        words = query.split()
        combined_results: List[SearchResult] = []

        for word in words:
            results = [s.search_for(word) for s in self.sonnets]

            if not combined_results:
                # First word: initialize combined_results
                combined_results = results
            else:
                # Merge with previous results
                for i in range(len(combined_results)):
                    combined_result = combined_results[i]
                    result = results[i]

                    if search_mode.upper() == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            combined_results[i] = combined_result.combine_with(result)
                        else:
                            # No match in one of them
                            combined_results[i].matches = 0
                    elif search_mode.upper() == "OR":
                        combined_results[i] = combined_result.combine_with(result)
                    else:
                        raise ValueError(f"Unknown search mode: {search_mode}")

        return combined_results
