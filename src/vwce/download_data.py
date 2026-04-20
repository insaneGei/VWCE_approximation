import requests
import openpyxl


def download_swda():
    # Download SWDA market allocation data
    url = (
        "https://www.ishares.com/uk/individual/en/products/251882/ishares-msci-world-ucits-etf-acc-fund/1535604580409.ajax?fileType=xls&fileName=iShares-Core-MSCI-World-UCITS-ETF_fund&dataType=fund"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.ishares.com/uk/individual/en/products/251882/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    filename = "portfolio_allocations/SWDA_allocation.xls"

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"File salvato: {filename}")
    return filename

def download_xmme():
        
    # Download XMME allocation file from iShares website

    url = (
        "https://etf.dws.com/etfdata/export/GBR/ENG/excel/product/constituent/IE00BTJRMP35/"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://etf.dws.com/",
    }

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    filename = "portfolio_allocations/XMME_allocation.xlsx"

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"File salvato: {filename}")
    return filename

def download_vwce():

    # VWCE is different: it doesn't have a direct excel download but instead i have to convert a json file to xlsx

    url = "https://www.nl.vanguard/gpx/graphql"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.nl.vanguard",
        "Referer": "https://www.nl.vanguard/professional/product/etf/equity/9679/ftse-all-world-ucits-etf-usd-accumulating",
        "apollographql-client-name": "gpx",
        "x-consumer-id": "nl0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    payload = {
        "operationName": "MarketAllocationGqlQuery",
        "variables": {"portIds": ["9679"]},
        "query": """query MarketAllocationGqlQuery($portIds: [String!]!) {
    funds(portIds: $portIds) {
        profile {
        fundFullName
        primaryMarketEquityClassification
        polarisPdtTypeIndicator
        marketOfDomicile
        __typename
        }
        marketAllocation {
        portId
        date
        countryCode
        countryName
        fundMktPercent
        holdingStatCode
        benchmarkMktPercent
        regionCode
        regionName
        __typename
        }
        __typename
    }
    }
    """
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    allocations = data["data"]["funds"][0]["marketAllocation"]

    # Tieni solo i dati FTSE (esclude duplicati MSCI)
    allocations = [a for a in allocations if a["holdingStatCode"].startswith("FT")]


    # Salva in Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Market Allocation"

    ws.append(["countryCode", "countryName", "regionCode", "regionName",
            "fundMktPercent", "benchmarkMktPercent", "date"])

    for item in allocations:
        ws.append([
            item["countryCode"],
            item["countryName"],
            item["regionCode"],
            item["regionName"],
            item["fundMktPercent"],
            item["benchmarkMktPercent"],
            item["date"],
        ])

    filename = "portfolio_allocations/VWCE_allocation.xlsx"
    wb.save(filename)
    print(f"File salvato: {filename}")
    return filename
