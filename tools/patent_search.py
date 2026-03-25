from duckduckgo_search import DDGS
from tools.web_scraper import scrape_url

# ---------------------------------
# Step 1: Web Snippet Search + Scraping
# ---------------------------------
def get_patent_results(query, max_results=5):
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
            
            for i, r in enumerate(results):
                title = r.get("title", "Unknown Title")
                snippet = r.get("body", "No description available.")
                link = r.get("href", "#")
                
                # Deeper scraping for top results
                content = ""
                if i < 3: # Scrape only the top 3 to keep it fast
                    print(f"📄 Deep searching result {i+1}...")
                    content = scrape_url(link, max_chars=2000)
                
                patents.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "content": content
                })
        
        print(f"✅ Successfully retrieved and scraped {len(patents)} web results.")
    except Exception as e:
        print("❌ Web search failed:", e)
        
    return patents


# ---------------------------------
# Step 2: Format context for LLM
# ---------------------------------
def format_patent_context(patents):
    if not patents:
        return "No patent search results found online."

    context = "\n--- TOP WEB SEARCH & BROWSER RESULTS ---\n"

    for i, p in enumerate(patents, 1):
        context += f"Result {i}\nTitle: {p['title']}\nLink: {p['link']}\n"
        if p['content']:
            context += f"Deep Context: {p['content']}\n\n"
        else:
            context += f"Snippet: {p['snippet']}\n\n"

    context += "--- END OF WEB RESULTS ---\n"
    return context