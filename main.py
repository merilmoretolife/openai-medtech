from fastapi import FastAPI, Query
import openai
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# OpenAI API Key (Replace with your actual key)
openai.api_key = "your-openai-api-key"

# **Regulatory Data Mapping**
regulatory_data = {
    "Knee Implant": {
        "ISO_13485": "Quality Management System: Compliance with ISO 13485 for risk management and post-market surveillance.",
        "EU_MDR": "Annex I, Chapter II: The knee implant must meet General Safety & Performance Requirements (GSPR). Mechanical strength testing per MDR 2017/745.",
        "ASTM": "ASTM F2083-6b: The knee implant dimensions must comply with ASTM F2083-6b.",
        "US_FDA": "FDA Regulation Number 888.3560: Knee prosthesis must meet 21 CFR Part 820 Design Controls."
    }
}

# **Function to Scrape US FDA Data**
def scrape_fda_data(device_name):
    fda_url = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpcd/classification.cfm?start_search=1&Search=Search&DeviceName={device_name.replace(' ', '+')}"
    response = requests.get(fda_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            regulation_number = soup.find("td", text="Regulation Number").find_next("td").text.strip()
            return f"FDA Regulation Number: {regulation_number}"
        except:
            return "No FDA classification found."
    return "Regulatory data not available."

@app.get("/api/device-requirements")
async def get_device_requirements(device_name: str = Query(..., description="Enter device name")):
    """Fetches Design Input - Functional & Performance Requirements for a medical device from EU MDR, ASTM, ISO 13485, and US FDA."""
    
    # **Fetch Data from AI API**
    prompt = f"Provide Design Input - Functional & Performance Requirements for {device_name} based on ISO 13485, EU MDR, ASTM, and US FDA regulations."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    requirements = response["choices"][0]["message"]["content"]

    # **Fetch Data from Local Regulatory Database**
    if device_name in regulatory_data:
        iso_13485 = regulatory_data[device_name].get("ISO_13485", "Not Available")
        eu_mdr = regulatory_data[device_name].get("EU_MDR", "Not Available")
        astm = regulatory_data[device_name].get("ASTM", "Not Available")
        us_fda = regulatory_data[device_name].get("US_FDA", "Not Available")
    else:
        iso_13485, eu_mdr, astm, us_fda = "Not Available", "Not Available", "Not Available", "Not Available"

    # **Fetch FDA Data (Live Scraping)**
    fda_info = scrape_fda_data(device_name)

    return {
        "device_name": device_name,
        "requirements": requirements,
        "ISO_13485": iso_13485,
        "EU_MDR": eu_mdr,
        "ASTM": astm,
        "US_FDA": us_fda,
        "FDA_Classification": fda_info
    }
