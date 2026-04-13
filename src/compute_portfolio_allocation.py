#imports
import pandas as pd
import numpy as np
from swda_xls_to_csv import *
from pathlib import Path
import download_data 
import update_spreadsheet 
import optimization_utils 
import pprint

def main():
    # Scarica i dati più recenti
    try:
        swda_path = download_data.download_swda()
    except Exception as e:
        print(f"Errore durante il download di SWDA: {e}")
    try: 
        xmme_path = download_data.download_xmme()
    except Exception as e:
        print(f"Errore durante il download di XMME: {e}")
    try:
        vwce_path = download_data.download_vwce()
    except Exception as e:
        print(f"Errore durante il download di VWCE: {e}")

    #convert swda xls to csv
    try:
        swda_csv_path = Path(swda_path).with_suffix('.csv')
        convert(Path(swda_path), swda_csv_path)
    except Exception as e:
        print(f"Errore durante la conversione di SWDA da XLS a CSV: {e}")

    #get portfolio geographical info for SWDA
    SWDA_alloc = pd.read_csv(swda_csv_path)

    SWDA_alloc = SWDA_alloc.rename(columns={'Weight (%)': 'Weight'})
    SWDA_alloc_geo = SWDA_alloc.groupby('Location')['Weight'].sum()
    SWDA_alloc_geo = SWDA_alloc_geo.rename(index = {'--': 'Other'})
    swda_countries = SWDA_alloc_geo.sort_index().index.tolist()

    #get portfolio geographical info for XMME
    df_temp = pd.read_excel(xmme_path, header=None)
    header_row_index = df_temp.index[df_temp.eq("Name").any(axis=1)].tolist()[0]
    XMME_alloc = pd.read_excel(xmme_path, skiprows=header_row_index, index_col = 0)
    XMME_alloc['Weighting'] = XMME_alloc['Weighting'].astype(float) * 100
    XMME_alloc = XMME_alloc.rename(columns={'Weighting': 'Weight (%)'})
    XMME_alloc_geo = XMME_alloc.groupby('Country')['Weight (%)'].sum()
    XMME_alloc_geo = XMME_alloc_geo.rename(index = {'-': 'Other'})
    xmme_countries = XMME_alloc_geo.sort_index().index.tolist()

    #get portfolio geographical info for VWCE
    VWCE_alloc_geo = pd.read_excel(vwce_path, header = 0)
    VWCE_alloc_geo = VWCE_alloc_geo.rename(columns={'fundMktPercent': 'Weight'})
    VWCE_alloc_geo = VWCE_alloc_geo.reset_index().set_index('countryName')['Weight']
    vwce_countries = VWCE_alloc_geo.sort_index().index.to_list()
    VWCE_alloc_geo.index.name = 'Country'

    #get sets of countries
    vwce_countries = set(vwce_countries)
    swda_countries = set(swda_countries)
    xmme_countries = set(xmme_countries)

    swda_xmme_countries = swda_countries.union(xmme_countries)

    pp = pprint.PrettyPrinter(indent=4, width=40)
    print('Countries in SWDA and XMME:')
    pp.pprint(swda_xmme_countries)
    print('\n')
    print('Countries in VWCE and not in SWDA/XMME:')
    pp.pprint(vwce_countries - swda_xmme_countries)  
    print('\n')   
    print('Countries in SWDA/XMME and not in VWCE:')
    pp.pprint(swda_xmme_countries - vwce_countries)
    print('\n')
    print('Countries in all three:')
    pp.pprint(swda_xmme_countries.intersection(vwce_countries))
    print('\n')

    # Fix a couple of name ambiguities in country names
    VWCE_alloc_geo = VWCE_alloc_geo.rename(index = {'United States of America': 'United States'})
    XMME_alloc_geo = XMME_alloc_geo.rename(index = {'Korea, Republic of': 'Korea'})

    #There is still eteronimy in the way South Korea and Russia are named in the three datasets
    if "South korea" in XMME_alloc_geo.index:
        XMME_alloc_geo.rename(index = {'South korea': 'Korea'})
    if "South Korea" in SWDA_alloc_geo.index:
        SWDA_alloc_geo.rename(index = {'South Korea': 'Korea'})
    if "South korea" in VWCE_alloc_geo.index:
        VWCE_alloc_geo.rename(index = {'South korea': 'Korea'})

    if "Russian Federation" in XMME_alloc_geo.index:
        XMME_alloc_geo.rename(index = {"Russian Federation": 'Russia'})
    if "Russian Federation" in SWDA_alloc_geo.index:
        SWDA_alloc_geo.rename(index = {"Russian Federation": 'Russia'})
    if "Russian Federation" in VWCE_alloc_geo.index:
        VWCE_alloc_geo.rename(index = {"Russian Federation": 'Russia'})

    df_etf = pd.DataFrame({
    'SWDA': SWDA_alloc_geo,
    'XMME': XMME_alloc_geo,
    'VWCE': VWCE_alloc_geo
    }).fillna(0).sort_values( by = 'VWCE', ascending = False)

    # compute optimal weights for SWDA and XMME with a linear programming algorithm
    optimal_weights = optimization_utils.compute_optimal_weights(df_etf)

    # compare the obtained allocation to VWCE
    balanced_allocation = optimal_weights[0] * df_etf['SWDA'] + optimal_weights[1] * df_etf['XMME']

    comparison_df = pd.DataFrame({
        'SWDA+XMME': balanced_allocation,
        'VWCE': df_etf['VWCE']
    })

    # update the spreadsheet with the new allocation and the comparison with VWCE
    try:
        update_spreadsheet.update_spreadsheet_with_allocation(optimal_weights, balanced_allocation, comparison_df)

    except Exception as e:
        print(f"Errore durante l'aggiornamento del foglio di calcolo: {e}")
   
    print("Fine run")

if __name__ == "__main__":
    main()