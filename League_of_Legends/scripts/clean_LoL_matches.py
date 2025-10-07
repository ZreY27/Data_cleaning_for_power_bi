import pandas as pd

# load raw data / charger les données brutes
raw_csv_path = "League_of_Legends/data/raw/"
cleaned_csv_path = "League_of_Legends/data/processed/"
df = pd.read_csv(raw_csv_path + "____.csv") # <-- fill the blank with your raw csv file name / remplir le blanc avec le nom de votre fichier csv brut

# delete unnecessary columns / supprimer les colonnes inutiles
df = df.drop(columns=["matchId", "queueId"], errors="ignore")

# correct data types / corriger les types de données
df["win"] = df["win"].astype(bool)
df["timePlayed"] = df["timePlayed"].astype(int)
df["kills"] = df["kills"].astype(int)
df["deaths"] = df["deaths"].astype(int)
df["assists"] = df["assists"].astype(int)
df["gold"] = df["gold"].astype(int)

# Add useful metrics / ajouter des métriques utiles
df["KDA"] = (df["kills"] + df["assists"]) / df["deaths"].replace(0, 1)
df["CS_per_min"] = df["cs"] / (df["timePlayed"] / 60)

# save cleaned data / sauvegarder les données nettoyées
df.to_csv(cleaned_csv_path + "matches_clean.csv", index=False)
