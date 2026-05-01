"""Trust scoring for property listings."""

from __future__ import annotations

from dataclasses import dataclass

from geoflow.entity import PropertyEntity


@dataclass
class TrustScore:
    overall: float
    owner_verified: float
    price_consistency: float
    listing_freshness: float
    community_match: float
    phone_valid: float


class PropertyTrustScorer:
    """Score trustworthiness of a property listing."""

    WEIGHTS = {
        "owner_verified": 0.30,
        "price_consistency": 0.25,
        "listing_freshness": 0.20,
        "community_match": 0.15,
        "phone_valid": 0.10,
    }

    def score(self, entity: PropertyEntity, market_avg: float = 0.0) -> TrustScore:
        # Owner verified: binary for now, could integrate WhatsApp response
        owner_verified = 1.0 if entity.is_owner_direct else 0.3

        # Price consistency: within 20% of market average
        price_consistency = 0.5
        if market_avg > 0 and entity.price_aed > 0:
            ratio = entity.price_aed / market_avg
            price_consistency = max(0.0, 1.0 - abs(1.0 - ratio) * 2)

        # Listing freshness: placeholder — could use scraped_at age
        listing_freshness = 0.7

        # Community match: does title mention community?
        community_match = 0.5
        if entity.community and entity.community.lower() in entity.title.lower():
            community_match = 1.0

        # Phone valid: has at least one normalized phone
        phone_valid = 1.0 if len(entity.phones) >= 1 else 0.0

        overall = (
            owner_verified * self.WEIGHTS["owner_verified"]
            + price_consistency * self.WEIGHTS["price_consistency"]
            + listing_freshness * self.WEIGHTS["listing_freshness"]
            + community_match * self.WEIGHTS["community_match"]
            + phone_valid * self.WEIGHTS["phone_valid"]
        )
        return TrustScore(
            overall=round(min(max(overall, 0.0), 1.0), 3),
            owner_verified=round(owner_verified, 3),
            price_consistency=round(price_consistency, 3),
            listing_freshness=round(listing_freshness, 3),
            community_match=round(community_match, 3),
            phone_valid=round(phone_valid, 3),
        )
