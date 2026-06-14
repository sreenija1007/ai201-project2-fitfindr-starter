"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

from tools import search_listings, suggest_outfit, create_fit_card

def run_agent(query: str, wardrobe: dict) -> dict:
    session = _new_session(query, wardrobe)
    
    # Step 2: Parse using string splits
    words = query.split()
    parsed_price = None
    parsed_size = None
    
    for i, word in enumerate(words):
        if word.startswith('$'):
            try:
                parsed_price = float(word.replace('$', '').replace(',', ''))
            except ValueError:
                pass
        if word.lower() == 'size' and i + 1 < len(words):
            parsed_size = words[i + 1].upper()
            
    session["parsed"] = {"description": query, "size": parsed_size, "max_price": parsed_price}
    
    # Step 3: Search
    results = search_listings(session["parsed"]["description"], session["parsed"]["size"], session["parsed"]["max_price"])
    session["search_results"] = results
    
    if len(results) == 0:
        session["error"] = "Nothing popped up! Try removing the price filter or changing your search terms."
        return session
        
    # Step 4, 5 & 6: Execute tools
    session["selected_item"] = results[0]
    session["outfit_suggestion"] = suggest_outfit(session["selected_item"], session["wardrobe"])
    session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])
    
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
