import os
from groq import Groq
from dotenv import load_dotenv 
from utils.data_loader import load_listings

load_dotenv() 

# Setup Groq client
ai_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
LLM_MODEL = "llama-3.3-70b-versatile"

def search_listings(description, size=None, max_price=None):
    all_items = load_listings()
    
    def is_match(item):
        desc_match = description.lower() in item.get('description', '').lower() or description.lower() in item.get('title', '').lower()
        size_match = True if not size else item.get('size') == size
        price_match = True if not max_price else item.get('price', 0) <= max_price
        
        return desc_match and size_match and price_match

    # Return filtered array
    return [item for item in all_items if is_match(item)]

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