from tools import search_listings, suggest_outfit, create_fit_card

def test_search_success_scenario():
    found = search_listings("vintage", size=None, max_price=150)
    assert type(found) is list

def test_search_failure_scenario():
    found = search_listings("impossible item that does not exist", size="XXS", max_price=1)
    assert len(found) == 0

def test_search_price_logic():
    found = search_listings("tee", size=None, max_price=30)
    for item in found:
        assert item["price"] <= 30

def test_outfit_empty_closet_handling():
    reply = suggest_outfit({"title": "Band Tee"}, {"items": []})
    assert "empty right now" in reply or "denim" in reply

def test_fit_card_blank_outfit_handling():
    reply = create_fit_card("", {"title": "Band Tee"})
    assert "taking a break" in reply