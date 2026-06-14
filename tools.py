import os
from groq import Groq
from dotenv import load_dotenv 
from utils.data_loader import load_listings

load_dotenv() 

# Setup Groq client
ai_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
LLM_MODEL = "llama-3.3-70b-versatile"

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    all_items = load_listings()
    valid_matches = []
    
    keywords = description.lower().split()

    for item in all_items:
        # Price check
        if max_price and item.get("price", 999999) > max_price:
            continue
            
        # Size check
        if size and size.lower() not in item.get("size", "").lower():
            continue

        # Calculate score based on tags, title, and description
        combined_text = f"{item.get('title', '')} {item.get('description', '')} {' '.join(item.get('style_tags', []))}".lower()
        
        match_score = sum(1 for word in keywords if word in combined_text)
        
        if match_score > 0:
            item_copy = item.copy()
            item_copy['_match_score'] = match_score
            valid_matches.append(item_copy)

    # Sort by the injected score key, then remove it before returning
    valid_matches.sort(key=lambda x: x['_match_score'], reverse=True)
    for match in valid_matches:
        del match['_match_score']
        
    return valid_matches

def suggest_outfit(new_item, wardrobe):
    # Early exit if the closet is completely empty
    if len(wardrobe.get("items", [])) == 0:
        return "I noticed your closet file is empty right now. For this piece, you can never go wrong pairing it with standard black denim and a clean pair of sneakers."
        
    system_instruction = "You are a helpful fashion stylist."
    user_request = f"Create an outfit using this new item: {new_item}. Base it on these existing clothes: {wardrobe}."
    
    chat_completion = ai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_request}
        ],
        temperature=0.7
    )
    return chat_completion.choices[0].message.content

def create_fit_card(outfit, new_item):
    # Early exit if the outfit text failed to generate
    if outfit == "":
        return f"Found a great {new_item.get('title')}! The styling AI is taking a break right now, but check out these item details."
        
    user_request = f"Write a casual, fun Instagram caption for this outfit idea: {outfit}. Mention the newly thrifted item: {new_item}. Keep it brief and use emojis."
    
    # Higher temperature for more creative variety
    chat_completion = ai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": user_request}],
        temperature=0.85
    )
    return chat_completion.choices[0].message.content