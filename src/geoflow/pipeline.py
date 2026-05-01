"""End-to-end GEO pipeline: scrape → entity → content → publish."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from geoflow.engine import GEOEngine
from geoflow.entity import EntityExtractor, PropertyEntity
from geoflow.publisher import MarkdownPublisher
from geoflow.trust import PropertyTrustScorer


class GEOFlowPipeline:
    """Orchestrate the full GEO workflow."""

    def __init__(
        self,
        output_dir: str = "./geo-content",
        min_trust: float = 0.0,
        market_avg: float = 0.0,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_trust = min_trust
        self.market_avg = market_avg
        self.extractor = EntityExtractor()
        self.scorer = PropertyTrustScorer()
        self.engine = GEOEngine()
        self.publisher = MarkdownPublisher(self.output_dir)
        self.stats: dict[str, Any] = {
            "scraped": 0,
            "entities": 0,
            "published": 0,
            "avg_trust": 0.0,
        }

    def run(
        self,
        listings: list[dict[str, Any]],
    ) -> list[Path]:
        """Process raw listings through the full GEO pipeline."""
        published: list[Path] = []
        trust_scores: list[float] = []

        for listing in listings:
            self.stats["scraped"] += 1

            entity = self.extractor.extract(
                raw_text=listing.get("text", ""),
                title=listing.get("title", ""),
                community=listing.get("community", ""),
                source_url=listing.get("url", ""),
                scraped_at=listing.get("scraped_at", ""),
            )
            self.stats["entities"] += 1

            trust = self.scorer.score(entity, market_avg=self.market_avg)
            trust_scores.append(trust.overall)

            if trust.overall < self.min_trust:
                continue

            content = self.engine.generate(entity, trust)
            path = self.publisher.write(entity, content)
            published.append(path)
            self.stats["published"] += 1

            time.sleep(0.1)  # Be polite

        self.stats["avg_trust"] = round(
            sum(trust_scores) / len(trust_scores), 3
        ) if trust_scores else 0.0

        self._write_manifest(published)
        return published

    def _write_manifest(self, published: list[Path]) -> None:
        manifest = {
            "stats": self.stats,
            "files": [str(p.relative_to(self.output_dir)) for p in published],
        }
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
