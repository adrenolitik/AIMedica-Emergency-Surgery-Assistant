import modal
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests

# Create a Modal app
app = modal.App("healthmate-clinic-lookup")

# Define the base image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "duckduckgo_search",
    "beautifulsoup4",
    "requests",
    "fastapi[standard]"
)

@app.function(image=image)
@modal.fastapi_endpoint()
def search_clinics(city: str) -> list:
    """
    Search for clinics near the specified city using DuckDuckGo.
    Returns a list of dictionaries containing clinic information.
    """
    if not city:
        return [{"error": "Please provide a city name"}]
    
    try:
        # Initialize DuckDuckGo search
        with DDGS() as ddgs:
            # Search for clinics
            search_query = f"top medical clinics near {city}"
            results = list(ddgs.text(search_query, max_results=3))
            
            if not results:
                return [{"error": f"No clinics found near {city}"}]
            
            # Process and format results
            clinics = []
            for result in results:
                clinic_info = {
                    "name": result.get("title", "Unknown Clinic"),
                    "link": result.get("link", "#"),
                    "description": result.get("body", "No description available")
                }
                clinics.append(clinic_info)
            
            return clinics
            
    except Exception as e:
        return [{"error": f"Error searching for clinics: {str(e)}"}]

@app.local_entrypoint()
def main():
    # Test the function locally
    results = search_clinics.remote("San Francisco")
    print(results) 


    