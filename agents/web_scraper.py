import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import json
import re
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class WebScraperAgent:
    """Agent for web scraping and data extraction"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str, extract_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape a single URL and extract data based on rules"""
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return {
                        "url": url,
                        "status": "error",
                        "error": f"HTTP {response.status}"
                    }
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Default extraction
                result = {
                    "url": url,
                    "status": "success",
                    "title": soup.title.string if soup.title else None,
                    "meta_description": None,
                    "headings": {},
                    "links": [],
                    "images": [],
                    "text_content": "",
                    "extracted_data": {}
                }
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    result["meta_description"] = meta_desc.get('content', '')
                
                # Extract headings
                for i in range(1, 4):
                    headings = soup.find_all(f'h{i}')
                    result["headings"][f'h{i}'] = [h.get_text(strip=True) for h in headings]
                
                # Extract links
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    result["links"].append({
                        "text": link.get_text(strip=True),
                        "url": absolute_url
                    })
                
                # Extract images
                for img in soup.find_all('img', src=True):
                    absolute_url = urljoin(url, img['src'])
                    result["images"].append({
                        "alt": img.get('alt', ''),
                        "src": absolute_url
                    })
                
                # Extract main text content
                for script in soup(["script", "style"]):
                    script.decompose()
                result["text_content"] = soup.get_text(separator=' ', strip=True)
                
                # Apply custom extraction rules if provided
                if extract_rules:
                    result["extracted_data"] = await self.apply_extraction_rules(
                        soup, extract_rules
                    )
                
                return result
                
        except asyncio.TimeoutError:
            return {
                "url": url,
                "status": "error",
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    async def apply_extraction_rules(self, soup: BeautifulSoup, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom extraction rules to soup"""
        
        extracted = {}
        
        for field_name, rule in rules.items():
            try:
                if isinstance(rule, str):
                    # Simple CSS selector
                    element = soup.select_one(rule)
                    extracted[field_name] = element.get_text(strip=True) if element else None
                
                elif isinstance(rule, dict):
                    selector = rule.get('selector', '')
                    attribute = rule.get('attribute', 'text')
                    multiple = rule.get('multiple', False)
                    
                    if multiple:
                        elements = soup.select(selector)
                        if attribute == 'text':
                            extracted[field_name] = [e.get_text(strip=True) for e in elements]
                        else:
                            extracted[field_name] = [e.get(attribute, '') for e in elements]
                    else:
                        element = soup.select_one(selector)
                        if element:
                            if attribute == 'text':
                                extracted[field_name] = element.get_text(strip=True)
                            else:
                                extracted[field_name] = element.get(attribute, '')
                        else:
                            extracted[field_name] = None
                            
            except Exception as e:
                logger.error(f"Error applying rule for {field_name}: {e}")
                extracted[field_name] = None
        
        return extracted
    
    async def scrape_multiple(self, urls: List[str], extract_rules: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently"""
        
        tasks = [self.scrape_url(url, extract_rules) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": urls[i],
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def extract_structured_data(self, url: str, schema_type: str = None) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, microdata, etc.)"""
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return {"status": "error", "error": f"HTTP {response.status}"}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                structured_data = {
                    "url": url,
                    "json_ld": [],
                    "microdata": [],
                    "opengraph": {}
                }
                
                # Extract JSON-LD
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        data = json.loads(script.string)
                        if schema_type and data.get('@type') != schema_type:
                            continue
                        structured_data["json_ld"].append(data)
                    except json.JSONDecodeError:
                        pass
                
                # Extract OpenGraph meta tags
                for meta in soup.find_all('meta', property=re.compile(r'^og:')):
                    property_name = meta.get('property', '').replace('og:', '')
                    structured_data["opengraph"][property_name] = meta.get('content', '')
                
                return structured_data
                
        except Exception as e:
            logger.error(f"Error extracting structured data from {url}: {e}")
            return {"status": "error", "error": str(e)}

async def run_web_scraper_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for the web scraper agent"""
    
    url = params.get("url", "")
    urls = params.get("urls", [])
    extract_rules = params.get("extract_rules", None)
    mode = params.get("mode", "simple")  # simple, structured, or custom
    
    if not url and not urls:
        return {
            "status": "error",
            "error": "No URL(s) provided"
        }
    
    async with WebScraperAgent() as scraper:
        try:
            if mode == "structured":
                # Extract structured data
                schema_type = params.get("schema_type")
                result = await scraper.extract_structured_data(url, schema_type)
                return {
                    "status": "completed",
                    "mode": "structured",
                    "data": result
                }
            
            elif urls:
                # Scrape multiple URLs
                results = await scraper.scrape_multiple(urls, extract_rules)
                return {
                    "status": "completed",
                    "mode": "multiple",
                    "count": len(results),
                    "results": results
                }
            
            else:
                # Scrape single URL
                result = await scraper.scrape_url(url, extract_rules)
                return {
                    "status": "completed",
                    "mode": "single",
                    "data": result
                }
                
        except Exception as e:
            logger.error(f"Web scraper agent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }