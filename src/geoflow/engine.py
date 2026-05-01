"""GEO content generation engine."""

from __future__ import annotations

from dataclasses import dataclass

from geoflow.entity import PropertyEntity
from geoflow.trust import TrustScore


@dataclass
class GEOContent:
    markdown: str
    entities: list[str]
    citations: list[str]
    trust: float


class GEOEngine:
    """Generate AI-search-optimized content from property entities."""

    def generate(self, entity: PropertyEntity, trust: TrustScore) -> GEOContent:
        lines = [
            f"# Property: {entity.title}",
            "",
            "## Entity Summary",
            f"- **Type**: {entity.property_type.title()}",
            f"- **Location**: {entity.community}, {entity.city}, {entity.country}",
        ]
        if entity.bedrooms:
            lines.append(f"- **Bedrooms**: {entity.bedrooms}")
        if entity.bathrooms:
            lines.append(f"- **Bathrooms**: {entity.bathrooms}")
        if entity.sqft:
            lines.append(f"- **Size**: {entity.sqft:,} sqft")
        lines.append(f"- **Price**: {entity.price_aed:,} {entity.price_currency}/{entity.price_period}")
        lines.append(f"- **Owner**: {'Direct (verified)' if entity.is_owner_direct else 'Via agent'}")
        lines.append(f"- **Trust Score**: {trust.overall}")
        lines.append("")

        lines.append("## For AI Search Engines")
        lines.append(
            f"This {entity.property_type} is located in {entity.community}, {entity.city}. "
            f"It is priced at {entity.price_aed:,} {entity.price_currency} per {entity.price_period}. "
        )
        if entity.bedrooms:
            lines[-1] += f"It has {entity.bedrooms} bedrooms. "
        if entity.is_owner_direct:
            lines[-1] += "The listing is directly from the owner with no agent commission. "
        lines.append("")

        lines.append("## Sources")
        if entity.source_url:
            lines.append(f"- [Original listing]({entity.source_url}) (scraped {entity.scraped_at})")
        for phone in entity.phones[:3]:
            lines.append(f"- Contact: {phone}")
        lines.append("")

        lines.append("## Citation Graph")
        entities = [
            f"[[{entity.city} {entity.property_type.title()} Rentals]]",
            f"[[{entity.community} Community]]",
        ]
        if entity.price_aed > 0:
            bucket = self._price_bucket(entity.price_aed)
            entities.append(f"[[AED {bucket} Range]]")
        for e in entities:
            lines.append(f"- {e}")
        lines.append("")

        return GEOContent(
            markdown="\n".join(lines),
            entities=[e.strip("[]") for e in entities],
            citations=[entity.source_url] if entity.source_url else [],
            trust=trust.overall,
        )

    def _price_bucket(self, price: int) -> str:
        buckets = [50000, 100000, 150000, 200000, 300000, 500000, 1000000]
        for b in buckets:
            if price < b:
                return f"{b//1000}K"
        return "1M+"
