from duckduckgo_search import DDGS

# ---------------------------------
# Step 1: Web Snippet Search
# ---------------------------------
def get_patent_results(query, max_results=10):
    print("🔎 Searching web for patents:", query)
    
    patents = []
    
    try:
        with DDGS() as ddgs:
            # Append 'patent' to ensure IP focus if it's missing
            if "patent" not in query.lower():
                search_query = f"{query} patent"
            else:
                search_query = query
                
            results = ddgs.text(search_query, max_results=max_results)
            
            for r in results:
                title = r.get("title", "Unknown Title")
                abstract = r.get("body", "No description available.")
                link = r.get("href", "#")
                
                patents.append({
                    "title": title,
                    "abstract": abstract,
                    "link": link
                })
        
        print(f"✅ Successfully retrieved {len(patents)} web results.")
    except Exception as e:
        print("❌ Web search failed:", e)
        
    return patents


# ---------------------------------
# Step 2: Format context for LLM
# ---------------------------------
def format_patent_context(patents):
    if not patents:
        return "No patent search results found online."

    context = "\n--- TOP 10 WEB SEARCH RESULTS ---\n"

    for i, p in enumerate(patents, 1):
        context += f"Result {i}\nTitle: {p['title']}\nLink: {p['link']}\nSnippet: {p['abstract']}\n\n"

    context += "--- END OF WEB RESULTS ---\n"
    return context