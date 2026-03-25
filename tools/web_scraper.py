import requests
from bs4 import BeautifulSoup
import re

def scrape_url(url, max_chars=3000):
    """
    Fetches the content of a URL and extracts clean text.
    - Fetches the HTML content.
    - Parses it using BeautifulSoup.
    - Removes scripts, styles, and other non-text elements.
    - Returns a cleaned string.
    """
    print(f"📄 Scraping content from: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Remove unwanted tags
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()
            
        # Get text
        text = soup.get_text(separator=' ')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit the response to prevent prompt bloat
        return text[:max_chars] + "..." if len(text) > max_chars else text
        
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return f"Error reading content: {str(e)}"

if __name__ == "__main__":
    # Test
    test_url = "https://www.google.com/patents/US1234567"
    print(scrape_url(test_url))
