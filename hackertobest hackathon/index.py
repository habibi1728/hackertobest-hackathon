import os
import zipfile
import urllib.request

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:,.2f}".format)
sns.set_theme(style="whitegrid")

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "OnlineRetail.csv")
XLSX_PATH = os.path.join(DATA_DIR, "Online Retail.xlsx")
UCI_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"

os.makedirs(DATA_DIR, exist_ok=True)

if os.path.exists(CSV_PATH):
    # Versi Kaggle: encoding bukan UTF-8
    df_raw = pd.read_csv(CSV_PATH, encoding="ISO-8859-1")
elif os.path.exists(XLSX_PATH):
    df_raw = pd.read_excel(XLSX_PATH)
else:
    zip_path = os.path.join(DATA_DIR, "online_retail.zip")
    urllib.request.urlretrieve(UCI_URL, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(DATA_DIR)
    df_raw = pd.read_excel(XLSX_PATH)

print("Shape data asli:", df_raw.shape)
df_raw.head()

df = df_raw.sample(frac=0.10, random_state=42).reset_index(drop=True)
print("Shape setelah sampling 10%:", df.shape)
df.head()

df.info()
print("Jumlah null per kolom:")
print(df.isnull().sum())
print()
print("Statistik deskriptif:")
df.describe()
print("Quantity <= 0   :", (df["Quantity"] <= 0).sum())
print("UnitPrice <= 0  :", (df["UnitPrice"] <= 0).sum())
print("Invoice 'C' (cancel/return):", df["InvoiceNo"].astype(str).str.startswith("C").sum())

before = len(df)
df_clean = df.dropna().copy()
print(f"Baris dihapus: {before - len(df_clean):,} ({(before - len(df_clean)) / before:.1%})")
print("Sisa null:", df_clean.isnull().sum().sum())

before = len(df_clean)
is_return = df_clean["InvoiceNo"].str.startswith("C") | (df_clean["Quantity"] <= 0)
df_clean = df_clean[~is_return]
print(f"Return dibuang: {before - len(df_clean):,}")

before = len(df_clean)
df_clean = df_clean[df_clean["UnitPrice"] > 0]
print(f"Free items dibuang: {before - len(df_clean):,}")
print("Shape setelah cleaning:", df_clean.shape)

df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
print(df_clean["InvoiceDate"].dtype)
print("Rentang tanggal:", df_clean["InvoiceDate"].min(), "->", df_clean["InvoiceDate"].max())

df_clean["Revenue"] = df_clean["Quantity"] * df_clean["UnitPrice"]
df_clean[["InvoiceNo", "Quantity", "UnitPrice", "Revenue"]].head()

print(f"Total revenue (sampel 10%): £{df_clean['Revenue'].sum():,.2f}")

top10 = (
    df_clean.groupby("Country", observed=True)["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

plt.figure(figsize=(10, 6))
ax = sns.barplot(data=top10, x="Revenue", y="Country", hue="Country",
                 palette="viridis", legend=False)

for container in ax.containers:
    ax.bar_label(container, labels=[f"£{v:,.0f}" for v in top10["Revenue"]], padding=3)

ax.set_title("Top 10 Negara by Total Revenue (Sampel 10%)", fontsize=14, weight="bold")
ax.set_xlabel("Total Revenue (£)")
ax.set_ylabel("")
plt.tight_layout()
plt.show()

uk_share = top10.loc[top10["Country"] == "United Kingdom", "Revenue"].sum() / df_clean["Revenue"].sum()
print(f"Negara dengan revenue tertinggi: {top10.loc[0, 'Country']}")
print(f"Kontribusi United Kingdom terhadap total revenue: {uk_share:.1%}")
print(f"Baris awal (sampel): {len(df):,} -> setelah cleaning: {len(df_clean):,}")