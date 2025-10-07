import requests
import pandas as pd
import os

API_KEY = "_________________________"  # ⚠️ Regenerate your key on https://developer.riotgames.com/
REGION = "____"  # Summoner endpoints = euw1, na1, eun1...
REGION_ROUTING = "____"  # Match endpoints = europe, americas, asia
SUMMONER_NAME = "_____" # Your summoner name / votre nom d'invocateur
TAGLINE = "___"  # The 3 digit tag after the summoner name / le tag de 3 lettres après le nom d'invocateur

# --- 1. Get Summoner info / Obtenir les infos de l'invocateur ---
url = f"https://{REGION_ROUTING}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{SUMMONER_NAME}/{TAGLINE}?api_key={API_KEY}"
response = requests.get(url)
print("Status code:", response.status_code)
summoner = response.json()
print("Summoner response:", summoner)

if "puuid" not in summoner:
    raise Exception(f"Error fetching summoner. Check API key, summoner name, or region. Response: {summoner}")

puuid = summoner["puuid"]

# --- 2. Get last 20 match IDs / Obtenir les 20 derniers IDs de match ---
url_matches = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={API_KEY}"
matches = requests.get(url_matches).json()
print(f"Fetched {len(matches)} matches")

# --- 3. Load existing matches if CSV exists / Charger les matchs existants si le CSV existe ---
csv_path = "lol_stats.csv"
if os.path.exists(csv_path):
    old_df = pd.read_csv(csv_path)
    old_match_ids = set(old_df["matchId"])
else:
    old_df = pd.DataFrame()
    old_match_ids = set()

# --- 4. Extract only new matches / Extraire seulement les nouveaux matchs ---
all_matches = []
for match_id in matches:
    if match_id in old_match_ids:
        continue  # Skip matches already in CSV
    url_match = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}"
    data = requests.get(url_match).json()

    if "info" not in data:
        print(f"Skipping match {match_id}, no 'info' field")
        continue

    for p in data["info"]["participants"]:
        if p["puuid"] == puuid:
            all_matches.append({
                "matchId": match_id,
                "champion": p["championName"],
                "kills": p["kills"],
                "deaths": p["deaths"],
                "assists": p["assists"],
                "win": p["win"],
                "cs": p["totalMinionsKilled"],
                "gold": p["goldEarned"],
                "timePlayed": p["timePlayed"],  # in seconds
                "gameMode": data["info"]["gameMode"],   # <-- add this
                "queueId": data["info"]["queueId"]      # <-- and this
        })

# --- 5. Append new matches and save / Ajouter les nouveaux matchs et sauvegarder ---
if all_matches:
    new_df = pd.DataFrame(all_matches)
    if not old_df.empty:
        final_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        final_df = new_df
    final_df.to_csv(csv_path, index=False)
    print(f"Added {len(all_matches)} new matches. CSV updated: {csv_path}")
else:
    print("No new matches to add.")