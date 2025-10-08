
import pandas as pd
import numpy as np

# ------------------ LOAD DATA / CHARGER LES DONNÉES ------------------
data = pd.read_csv("World_Development_Indicators/data/raw/WDIData.csv")
series = pd.read_csv("World_Development_Indicators/data/raw/WDISeries.csv")
countries = pd.read_csv("World_Development_Indicators/data/raw/WDICountry.csv")

# ------------------ CLEAN SERIES / NETTOYER LES SÉRIES ------------------
# Keep only useful columns
series = series[['Series Code', 'Indicator Name', 'Indicator Description']]
series.columns = ['indicator_code', 'indicator_name', 'indicator_description']

# Filter environmental indicators using keywords / Filtrer les indicateurs environnementaux avec des mots-clés
env_keywords = [
    'CO2', 'carbon', 'emission', 'energy', 'environment', 'pollution', 'climate',
    'forest', 'biodiversity', 'renewable', 'water', 'temperature', 'agriculture',
    'waste', 'fuel', 'deforestation'
]
series_env = series[series['indicator_name'].str.contains('|'.join(env_keywords), case=False, na=False)]

# ------------------ CLEAN MAIN DATA / NETTOYER LES DONNÉES PRINCIPALES ------------------
# Keep only relevant columns (country, code, indicator, years) / Garder seulement les colonnes pertinentes (pays, code, indicateur, années)
data = data.rename(columns={
    'Country Name': 'country_name',
    'Country Code': 'country_code',
    'Indicator Name': 'indicator_name',
    'Indicator Code': 'indicator_code'
})

# Keep only environmental indicators (based on series_env) / Garder seulement les indicateurs environnementaux (basé sur series_env)
data_env = data[data['indicator_code'].isin(series_env['indicator_code'])]

# Melt data from wide to long format / Transformer les données de format large à long
data_env_long = data_env.melt(
    id_vars=['country_name', 'country_code', 'indicator_name', 'indicator_code'],
    var_name='year',
    value_name='value'
)

# Clean and convert years / Nettoyer et convertir les années
data_env_long['year'] = pd.to_numeric(data_env_long['year'], errors='coerce')
data_env_long = data_env_long.dropna(subset=['year', 'value'])
data_env_long['value'] = pd.to_numeric(data_env_long['value'], errors='coerce')

# ------------------ CLEAN COUNTRIES / NETTOYER LES PAYS ------------------
countries = countries.rename(columns={
    'TableName': 'country_name',
    'Region': 'region',
    'IncomeGroup': 'income_group'
})
countries = countries[['Country Code', 'country_name', 'region', 'income_group']]
countries.columns = ['country_code', 'country_name', 'region', 'income_group']

# ------------------ MERGE DATA / FUSIONNER LES DONNÉES ------------------
merged = pd.merge(
    data_env_long,
    countries,
    on='country_code',
    how='left'
)

# ------------------ FINAL TOUCHES / TOUCHES FINALES ------------------
merged = merged.drop_duplicates(subset=['country_code', 'indicator_code', 'year'])
merged = merged.sort_values(by=['country_name', 'indicator_name', 'year'])

# Add continent-level aggregation (optional) / Ajouter une agrégation au niveau du continent (optionnel)
continent_data = merged.groupby(['region', 'indicator_name', 'year'], as_index=False)['value'].mean()
continent_data['country_name'] = continent_data['region']
continent_data['country_code'] = 'REGION'

final = pd.concat([merged, continent_data], ignore_index=True)

# ------------------ EXPORT / EXPORTER ------------------
final.to_csv("World_Development_Indicators/data/processed/wdi_environment_clean.csv", index=False, encoding='utf-8-sig')

print("✅ Cleaned file saved: wdi_environment_clean.csv")
print(f"Total rows: {len(final):,}")
print("Preview:")
print(final.head())
