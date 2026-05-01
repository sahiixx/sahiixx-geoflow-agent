"""Publish GEO content as structured markdown."""

from __future__ import annotations

from pathlib import Path

from geoflow.engine import GEOContent
from geoflow.entity import PropertyEntity


class MarkdownPublisher:
    """Write GEO content cards to markdown files."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, entity: PropertyEntity, content: GEOContent) -> Path:
        """Write a single property card."""
        safe_name = self._safe_filename(entity.community, entity.id)
        path = self.output_dir / f"{safe_name}.md"
        path.write_text(content.markdown, encoding="utf-8")
        return path

    def write_index(self, entries: list[tuple[PropertyEntity, GEOContent]]) -> Path:
        """Write an index of all published properties."""
        lines = [
            "# GEO Content Index",
            "",
            f"Total properties: {len(entries)}",
            "",
            "| Property | Community | Price | Trust |",
            "|----------|-----------|-------|-------|",
        ]
        for entity, content in entries:
            lines.append(
                f"| [{entity.title}]({self._safe_filename(entity.community, entity.id)}.md) "
                f"| {entity.community} | {entity.price_aed:,} AED | {content.trust} |"
            )
        path = self.output_dir / "index.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def _safe_filename(community: str, entity_id: str) -> str:
        base = f"{community}_{entity_id}".lower()
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in base)
        return safe[:80]
