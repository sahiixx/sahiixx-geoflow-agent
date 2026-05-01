"""Extract structured entities from raw real estate listings."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PropertyEntity:
    """A structured real estate property."""

    id: str
    title: str
    community: str
    city: str = "Dubai"
    country: str = "UAE"
    price_aed: int = 0
    price_currency: str = "AED"
    price_period: str = "year"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    sqft: Optional[int] = None
    property_type: str = "unknown"  # villa, apartment, townhouse, etc.
    is_owner_direct: bool = False
    phones: list[str] = field(default_factory=list)
    source_url: str = ""
    scraped_at: str = ""
    raw_text: str = ""


class EntityExtractor:
    """Extract PropertyEntity from scraped text."""

    def __init__(self) -> None:
        self.phone_re = re.compile(
            r"(?:\+971|00971|971)?\s*5[0-9]\s*(?:\d{3}\s*\d{4}|\d{2}\s*\d{3}\s*\d{2})"
        )
        self.price_re = re.compile(r"AED\s*([\d,]+)")
        self.owner_keywords = [
            "owner", "direct", "no commission", "landlord",
            "direct from owner", "owner direct", "no agent",
            "private", "مالك", "بدون عمولة",
        ]
        self.type_keywords = {
            "villa": ["villa", "villas"],
            "apartment": ["apartment", "apartments", "flat", "flats"],
            "townhouse": ["townhouse", "townhouses", "town home"],
            "studio": ["studio", "studios"],
            "penthouse": ["penthouse", "penthouses"],
        }

    def extract(self, raw_text: str, title: str = "", community: str = "", source_url: str = "", scraped_at: str = "") -> PropertyEntity:
        text_lower = raw_text.lower()

        # Price
        price_match = self.price_re.search(raw_text)
        price = 0
        if price_match:
            try:
                price = int(price_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Phones
        phones = []
        for m in self.phone_re.finditer(raw_text):
            normalized = self._normalize_phone(m.group())
            if normalized and normalized not in phones:
                phones.append(normalized)

        # Owner direct
        is_owner = any(kw in text_lower for kw in self.owner_keywords)

        # Property type
        prop_type = "unknown"
        for ptype, keywords in self.type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                prop_type = ptype
                break

        # Bedrooms
        beds = self._extract_number_hyphen(raw_text, ["bed", "bedroom", "br"])
        if beds is None:
            beds = self._extract_number(raw_text, [r"(\d+)\s*bed", r"(\d+)\s*br", r"(\d+)\s*bedroom"])
        baths = self._extract_number_hyphen(raw_text, ["bath", "bathroom", "ba"])
        if baths is None:
            baths = self._extract_number(raw_text, [r"(\d+)\s*bath", r"(\d+)\s*ba", r"(\d+)\s*bathroom"])
        sqft = self._extract_number(raw_text, [r"(\d+,?\d*)\s*sq\.?\s*ft", r"(\d+,?\d*)\s*sqft"])

        entity_id = re.sub(r"[^a-zA-Z0-9]", "_", f"{community}_{title}").lower()[:64]

        return PropertyEntity(
            id=entity_id,
            title=title[:120] if title else "Untitled",
            community=community,
            price_aed=price,
            property_type=prop_type,
            is_owner_direct=is_owner,
            phones=phones,
            source_url=source_url,
            scraped_at=scraped_at,
            raw_text=raw_text[:2000],
            bedrooms=beds,
            bathrooms=baths,
            sqft=sqft,
        )

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"\D", "", phone)
        if digits.startswith("971") and len(digits) == 12:
            return "+" + digits
        if digits.startswith("0") and len(digits) == 10:
            return "+971" + digits[1:]
        if digits.startswith("5") and len(digits) == 9:
            return "+971" + digits
        return ""

    def _extract_number(self, text: str, patterns: list[str]) -> Optional[int]:
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                try:
                    return int(m.group(1).replace(",", ""))
                except ValueError:
                    continue
        return None

    def _extract_number_hyphen(self, text: str, keywords: list[str]) -> Optional[int]:
        for kw in keywords:
            pat = rf"(\d+)\s*[-]?\s*{kw}"
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                try:
                    return int(m.group(1))
                except ValueError:
                    continue
        return None
