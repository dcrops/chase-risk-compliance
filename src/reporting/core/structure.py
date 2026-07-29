from dataclasses import dataclass
from typing import List


@dataclass
class SectionSpec:
    title: str
    level: int  # 1 = h2, 2 = h3, 3 = h4
    content: str


class ReportStructure:
    def __init__(self):
        self._sections: List[SectionSpec] = []

    def add(self, title: str, level: int, content: str):
        self._sections.append(SectionSpec(title, level, content))

    from dataclasses import dataclass
from typing import List


@dataclass
class SectionSpec:
    title: str
    level: int  # 1 = h2, 2 = h3, 3 = h4
    content: str


class ReportStructure:
    def __init__(self):
        self._sections: List[SectionSpec] = []

    def add(self, title: str, level: int, content: str):
        self._sections.append(SectionSpec(title, level, content))

    def render_markdown(self) -> str:
        lines: List[str] = []
        counters: dict[int, int] = {}

        page_break_titles = {
            "Executive Summary",
            "Coverage & Data Dependency Insight",
            "Data Sources",
            "Scope & Methodology",
            "Module Summary Overview",
            "Appendices",
        }

        for section in self._sections:
            level = section.level

            counters[level] = counters.get(level, 0) + 1

            for deeper_level in list(counters.keys()):
                if deeper_level > level:
                    counters[deeper_level] = 0

            number_parts = [
                str(counters[lvl])
                for lvl in sorted(counters.keys())
                if lvl <= level and counters[lvl] > 0
            ]
            number = ".".join(number_parts)

            heading_text = f"{number}. {section.title}"

            if level == 1:
                if section.title in page_break_titles:
                    heading = f'<h2 class="page-break-before">{heading_text}</h2>'
                else:
                    heading = f"<h2>{heading_text}</h2>"
            elif level == 2:
                heading = f"<h3>{heading_text}</h3>"
            elif level == 3:
                heading = f"<h4>{heading_text}</h4>"
            else:
                heading_level = min(level + 1, 6)
                heading = f"<h{heading_level}>{heading_text}</h{heading_level}>"

            lines.append(heading)
            lines.append("")

            content = section.content.strip()
            if content:
                lines.append(content)
                lines.append("")

        return "\n".join(lines)