"""Tests for GEOFlow Agent."""

from geoflow.entity import EntityExtractor, PropertyEntity
from geoflow.engine import GEOEngine
from geoflow.trust import PropertyTrustScorer


def test_extract_property():
    extractor = EntityExtractor()
    text = """
    Stunning 3-bedroom villa in The Springs for AED 135,000 per year.
    Direct from owner — no commission. Contact 050 123 4567.
    """
    entity = extractor.extract(
        raw_text=text,
        title="Beautiful Villa in Springs",
        community="The Springs",
        source_url="https://example.com/1",
        scraped_at="2026-04-26",
    )
    assert entity.community == "The Springs"
    assert entity.price_aed == 135000
    assert entity.is_owner_direct is True
    assert len(entity.phones) == 1
    assert entity.bedrooms == 3
    assert entity.property_type == "villa"


def test_trust_scoring():
    entity = PropertyEntity(
        id="test_1",
        title="Test",
        community="Springs",
        price_aed=135000,
        is_owner_direct=True,
        phones=["+971501234567"],
    )
    scorer = PropertyTrustScorer()
    trust = scorer.score(entity, market_avg=140000)
    assert 0.0 <= trust.overall <= 1.0
    assert trust.phone_valid == 1.0
    assert trust.owner_verified == 1.0


def test_geo_content():
    entity = PropertyEntity(
        id="test_1",
        title="Villa in Springs",
        community="The Springs",
        price_aed=135000,
        is_owner_direct=True,
        bedrooms=3,
        property_type="villa",
        phones=["+971501234567"],
        source_url="https://example.com/1",
        scraped_at="2026-04-26",
    )
    scorer = PropertyTrustScorer()
    trust = scorer.score(entity, market_avg=140000)
    engine = GEOEngine()
    content = engine.generate(entity, trust)
    assert "Villa in Springs" in content.markdown
    assert "135,000" in content.markdown
    assert "Trust Score" in content.markdown
    assert content.trust > 0
    assert len(content.entities) > 0
