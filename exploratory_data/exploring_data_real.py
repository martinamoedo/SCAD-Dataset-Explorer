import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Files paths
africa_file = "C:/Users/diego/OneDrive/Escritorio/Proyecto Scad/exploratory_data/SCAD2018Africa_Final.csv"
latam_file  = "C:/Users/diego/OneDrive/Escritorio/Proyecto Scad/exploratory_data/SCAD2018LatinAmerica_Final.csv"

# -----------------------------
# Helpers
# -----------------------------

def _replace_cat_missing(df: pd.DataFrame, cols: list[str], fill_value: str = "Missing") -> pd.DataFrame:
    """Fill NaN with `fill_value` and normalize literal 'Unknown' → `fill_value` in selected categorical cols."""
    for c in cols:
        if c in df.columns:
            df[c] = df[c].fillna(fill_value)
            df[c] = df[c].replace({"Unknown": fill_value})
    return df


def try_parse_series(s: pd.Series, fmts: list[str]) -> pd.Series:
    """Try multiple datetime formats after cleaning odd tokens; keep first successful parse per element (datetime64[ns])."""
    s_clean = s.astype(str).str.strip()
    s_clean = s_clean.replace({"[]": np.nan, "Unknown": np.nan})
    s_clean = s_clean.mask(s_clean.isin(["", "nan", "NaN", "None"]))

    out = pd.Series(pd.NaT, index=s_clean.index, dtype="datetime64[ns]")
    for fmt in fmts:
        need = out.isna()
        if not need.any():
            break
        parsed = pd.to_datetime(s_clean.where(need), format=fmt, errors="coerce")
        out = out.mask(need, parsed)

    # Fallback: general parser (dateutil)
    fallback = pd.to_datetime(s_clean, errors="coerce", dayfirst=True)
    out = out.fillna(fallback)

    return pd.to_datetime(out, errors="coerce")


def build_date_from_parts(row, y_col, m_col, d_col):
    """Construct Timestamp from (year, month, day) parts with tolerance to junk values."""
    y = pd.to_numeric(row.get(y_col, np.nan), errors="coerce")
    m = pd.to_numeric(row.get(m_col, np.nan), errors="coerce")
    d = pd.to_numeric(row.get(d_col, np.nan), errors="coerce")

    if pd.notna(y):
        y = int(y)
        m = int(m) if pd.notna(m) and 1 <= int(m) <= 12 else 1
        d = int(d) if pd.notna(d) and 1 <= int(d) <= 31 else 1
        try:
            return pd.Timestamp(year=y, month=m, day=d)
        except Exception:
            return pd.NaT
    return pd.NaT

# -----------------------------
# Load datasets
# -----------------------------
africa = pd.read_csv(africa_file, encoding="latin-1")
latam = pd.read_csv(latam_file, encoding="latin-1")

# -----------------------------
# EDA
# -----------------------------
# Preview first rows
print("Africa:")
print(africa.head(), "\n")

print("Latin America:")
print(latam.head(), "\n")

# Show dimensions
print("Africa shape:", africa.shape)
print("Latin America shape:", latam.shape)

# Show columns names
print("\nAfrica columns:", africa.columns.tolist())
print("\nLatin America columns:", latam.columns.tolist())

# Check missing values (percentage)
print("Missing values in Africa dataset:")
print((africa.isnull().mean() * 100).sort_values(ascending=False).head(15), "\n")

print("Missing values in Latin America dataset:")
print((latam.isnull().mean() * 100).sort_values(ascending=False).head(15), "\n")

# Data types
print("Africa dtypes:")
print(africa.dtypes.value_counts(), "\n")

print("Latin America dtypes:")
print(latam.dtypes.value_counts(), "\n")

# Unique values for some key columns
for col in ["countryname", "etype", "actor1", "target1"]:
    if col in africa.columns:
        print(f"Africa - {col}: {africa[col].nunique()} unique values")
        print(africa[col].value_counts().head(10), "\n")
    if col in latam.columns:
        print(f"Latin America - {col}: {latam[col].nunique()} unique values")
        print(latam[col].value_counts().head(10), "\n")

# -----------------------------
# Missing values handling (keep output structure/texts)
# -----------------------------
# Drop columns with 90%+ missing values (given list)
drop_cols = ["actor3", "issue3", "geo_comments", "location_precision"]
africa = africa.drop(columns=drop_cols, errors="ignore")
latam = latam.drop(columns=drop_cols, errors="ignore")

# Impute ndeath: NaN -> 0 (numeric rule)
for df in [africa, latam]:
    if "ndeath" in df.columns:
        df["ndeath"] = pd.to_numeric(df["ndeath"], errors="coerce").fillna(0).astype(int)

# Impute key categorical columns with "Missing" (also convert literal 'Unknown' → 'Missing')
cat_impute = ["actor1", "target1", "escalation", "issuenote", "nsource"]
for df in [africa, latam]:
    _replace_cat_missing(df, cat_impute, fill_value="Missing")

# Check again missing values summary
print("Africa missing values after cleaning:")
print(africa.isnull().mean().sort_values(ascending=False).head(10), "\n")

print("Latin America missing values after cleaning:")
print(latam.isnull().mean().sort_values(ascending=False).head(10))

# Standardize column names
africa = africa.rename(columns={"lgtbq_issue": "lgbtq_issue"})
latam = latam.rename(columns={"lgtbq_issue": "lgbtq_issue"})

# Add region column
africa["region"] = "Africa"
latam["region"] = "LatinAmerica"

# Concatenate datasets
scal_global = pd.concat([africa, latam], ignore_index=True)

# Check
print("Combined dataset shape:", scal_global.shape)
print(scal_global["region"].value_counts())
print(scal_global.head())

# Distribution of event types
print("Event types distribution (combined):")
print(scal_global["etype"].value_counts(dropna=False))

# Distribution by region
print("\nEvent types by region:")
print(scal_global.groupby("region")["etype"].value_counts().unstack(fill_value=0))

# Deaths
print("\nDeth summary statistics:")
print(scal_global["ndeath"].describe())

# Check how many events have no deaths vs at least one death
print("\nEvents with deaths vs no deaths:")
print((scal_global["ndeath"] > 0).value_counts())

# Top 10 deadliest events
print("\nTop 10 deadliest events:")
print(
    scal_global[["countryname", "startdate", "ndeath", "actor1", "target1"]]
    .sort_values(by="ndeath", ascending=False)
    .head(10)
)

# -----------------------------
# Date parsing (robust) + temporal features used by plots
# -----------------------------
# Robust parse using multiple formats; then fallback from parts
_date_formats = [
    "%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"
]
scal_global["startdate_fix"] = try_parse_series(scal_global["startdate"], _date_formats)
scal_global["enddate_fix"] = try_parse_series(scal_global["enddate"], _date_formats)

need_start = scal_global["startdate_fix"].isna()
scal_global.loc[need_start, "startdate_fix"] = scal_global.loc[need_start].apply(
    lambda r: build_date_from_parts(r, "styr", "stmo", "stday"), axis=1
)

need_end = scal_global["enddate_fix"].isna()
scal_global.loc[need_end, "enddate_fix"] = scal_global.loc[need_end].apply(
    lambda r: build_date_from_parts(r, "eyr", "emo", "eday"), axis=1
)

# Use the fixed dates going forward and FORCE datetime dtype
scal_global["startdate"] = pd.to_datetime(scal_global["startdate_fix"], errors="coerce")
scal_global["enddate"]   = pd.to_datetime(scal_global["enddate_fix"],   errors="coerce")
scal_global = scal_global.drop(columns=["startdate_fix", "enddate_fix"], errors="ignore")

# Extract year safely
scal_global["event_year"] = scal_global["startdate"].dt.year

# --- Events per year (total and by region) ---
events_per_year = scal_global.groupby("event_year").size()
events_by_region = (
    scal_global.groupby(["event_year", "region"]).size().unstack(fill_value=0)
)

# --- Deaths per year (total and by region) ---
# Clean negative values in ndeath
scal_global["ndeath"] = pd.to_numeric(scal_global["ndeath"], errors="coerce").fillna(0)
scal_global["ndeath"] = scal_global["ndeath"].apply(lambda x: max(x, 0))

deaths_per_year = scal_global.groupby("event_year")["ndeath"].sum()

deaths_by_region = (
    scal_global.groupby(["event_year", "region"])["ndeath"].sum().unstack(fill_value=0)
)

# --- Plots ---
plt.figure(figsize=(12, 5))
events_per_year.plot(kind="line", marker="o", title="Events per year (total)")
plt.ylabel("Number of events")
plt.show()

plt.figure(figsize=(12, 5))
events_by_region.plot(kind="line", marker="o", title="Events per year by region")
plt.ylabel("Number of events")
plt.show()

plt.figure(figsize=(12, 5))
deaths_per_year.plot(kind="line", marker="o", title="Deaths per year (total)")
plt.ylabel("Number of deaths")
plt.show()

plt.figure(figsize=(12, 5))
deaths_by_region.plot(kind="line", marker="o", title="Deaths per year by region")
plt.ylabel("Number of deaths")
plt.show()

# --- Events per country ---
events_country = scal_global["countryname"].value_counts().head(10)
print("Top 10 countries by number of events:")
print(events_country)

# --- Deaths per country ---
deaths_country = (
    scal_global.groupby("countryname")["ndeath"].sum().sort_values(ascending=False).head(10)
)
print("\nTop 10 countries by number of deaths:")
print(deaths_country)

# --- Event types per country (top 5 countries by events) ---
event_types_country = (
    scal_global.groupby(["countryname", "etype"]).size().unstack(fill_value=0)
)
print("\nEvent types distribution for top 5 countries:")
print(event_types_country.loc[events_country.index].head(5))

# --- Main actors per country (example: Nigeria & Mexico) ---
for country in ["Nigeria", "Mexico"]:
    print(f"\nTop actors in {country}:")
    print(scal_global[scal_global["countryname"] == country]["actor1"].value_counts().head(10))

# --- Main targets per country (example: Nigeria & Mexico) ---
for country in ["Nigeria", "Mexico"]:
    print(f"\nTop targets in {country}:")
    print(scal_global[scal_global["countryname"] == country]["target1"].value_counts().head(10))

# --- 1. Deaths by event type ---
deaths_by_etype = scal_global.groupby("etype")["ndeath"].sum().sort_values(ascending=False)
print("Deaths by event type:")
print(deaths_by_etype)

plt.figure(figsize=(10, 5))
sns.barplot(x=deaths_by_etype.index, y=deaths_by_etype.values)
plt.title("Total deaths by event type")
plt.xlabel("Event type (etype)")
plt.ylabel("Total deaths")
plt.show()

# --- 2. Actor vs Target (top 10) ---
actor_target = (
    scal_global.groupby(["actor1", "target1"]).size().reset_index(name="count").sort_values("count", ascending=False).head(10)
)
print("\nTop 10 Actor-Target pairs:")
print(actor_target)

plt.figure(figsize=(12, 6))
sns.barplot(data=actor_target, x="count", y="actor1", hue="target1")
plt.title("Top Actor-Target pairs")
plt.xlabel("Event count")
plt.ylabel("Actor")
plt.legend(title="Target", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.show()

# --- 3. Event types by region ---
etype_region = scal_global.groupby(["region", "etype"]).size().unstack(fill_value=0)
print("\nEvent types by region:")
print(etype_region)

etype_region.T.plot(kind="bar", figsize=(12, 6))
plt.title("Event types distribution by region")
plt.xlabel("Event type (etype)")
plt.ylabel("Number of events")
plt.show()

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
# 1) Temporal variables (reuse parsed dates)
scal_global["event_month"] = scal_global["startdate"].dt.month
end_for_duration = scal_global["enddate"].fillna(scal_global["startdate"])
scal_global["duration_days"] = (end_for_duration - scal_global["startdate"]).dt.days + 1

# 2) Deaths
scal_global["ndeath_clean"] = scal_global["ndeath"].replace([-99, -88, -77], np.nan)
scal_global["violent_event"] = (scal_global["ndeath_clean"] > 0).astype(int)
scal_global["mass_casualty"] = (scal_global["ndeath_clean"] >= 100).astype(int)

# 3) Participation
if "npart" in scal_global.columns:
    scal_global["npart_clean"] = scal_global["npart"].replace([-99, -88, -77], np.nan)
    # Impute numeric NaNs to 0 as requested
    scal_global["npart_clean"] = pd.to_numeric(scal_global["npart_clean"], errors="coerce").fillna(0)
    scal_global["mass_participation"] = (scal_global["npart_clean"] >= 4).astype(int)

# 4) Repression
repress_map = {0: "None", 1: "Non-lethal", 2: "Lethal"}
scal_global["repression_level"] = scal_global.get("repress").map(repress_map) if "repress" in scal_global.columns else np.nan
scal_global["repression_event"] = (scal_global.get("repress", pd.Series(0)).fillna(0) > 0).astype(int)

# 5) Event type (etype)
etype_map = {
    1: "Protest",
    2: "Riot",
    3: "Strike",
    4: "Demonstration (anti-gov)",
    5: "Demonstration (pro-gov)",
    6: "Repression",
    7: "Sectarian violence",
    8: "Communal violence",
    9: "Unidentified violence",
    10: "Other",
    -9: "Unknown",
}
scal_global["event_type_label"] = scal_global.get("etype").map(etype_map) if "etype" in scal_global.columns else np.nan

# === Feature Engineering – Part 2 ===
# Hygiene
if "region" in scal_global.columns:
    scal_global["region"] = scal_global["region"].astype(str).str.strip()
    scal_global["region"] = scal_global["region"].replace({
        "África": "Africa",
        "Africa ": "Africa",
        "Latin America": "LatinAmerica",
        "LatAm": "LatinAmerica",
    })

# Avoid double counting if sublocal present (keep first)
if "sublocal" in scal_global.columns:
    scal_global = scal_global[scal_global["sublocal"].fillna(1).astype(int) == 1].copy()

# Event type labels from SCAD 3.3
etype_label_map = {
    1: "Organized Demonstration",
    2: "Spontaneous Demonstration",
    3: "Organized Violent Riot",
    4: "Spontaneous Violent Riot",
    5: "General Strike",
    6: "Limited Strike",
    7: "Pro-Government Violence (Repression)",
    8: "Anti-Government Violence",
    9: "Extra-Government Violence",
    10: "Intra-Government Violence",
    -9: "Armed Conflict Placeholder (ACD)",
}
scal_global["etype_label"] = scal_global.get("etype").map(etype_label_map) if "etype" in scal_global.columns else np.nan

# Macro buckets
def bucket_event_family(e):
    if e in (1, 2, 5, 6):
        return "Demonstration/Strike (mostly non-violent)"
    if e in (3, 4):
        return "Riots (violent)"
    if e == 7:
        return "State/Pro-Gov Violence"
    if e == 8:
        return "Anti-Gov Insurgent Violence"
    if e == 9:
        return "Non-State Communal/Extra-Gov Violence"
    if e == 10:
        return "Intra-Gov Violence"
    if e == -9:
        return "ACD Placeholder"
    return "Other/Unknown"

scal_global["etype_family"] = scal_global.get("etype", pd.Series(np.nan)).apply(bucket_event_family)

# Issues safeguard
for col in ["issue1", "issue2", "issue3"]:
    if col not in scal_global.columns:
        scal_global[col] = np.nan

issue_label_map = {
    1: "Elections",
    2: "Economy/Jobs",
    3: "Food/Water/Subsistence",
    4: "Environmental Degradation",
    5: "Ethnic Issues/Discrimination",
    6: "Religious Issues/Discrimination",
    7: "Education",
    8: "Foreign Relations",
    9: "Domestic War/Violence/Terrorism",
    10: "Human Rights/Democracy",
    11: "Pro-Government",
    12: "Economic Resources/Assets",
    13: "Other",
    14: "Unknown/Not specified",
}
for col in ["issue1", "issue2", "issue3"]:
    scal_global[f"{col}_label"] = scal_global[col].map(issue_label_map)

# First non-null issue label
scal_global["issue_main"] = (
    scal_global[["issue1_label", "issue2_label", "issue3_label"]]
    .bfill(axis=1)
    .iloc[:, 0]
)

# Binary flags
scal_global["issue_election"] = (
    scal_global[["issue1", "issue2", "issue3"]].apply(lambda r: any(x == 1 for x in r if pd.notna(x)), axis=1)
).astype(int)
scal_global["issue_economy"] = (
    scal_global[["issue1", "issue2", "issue3"]].apply(lambda r: any(x == 2 for x in r if pd.notna(x)), axis=1)
).astype(int)
scal_global["issue_identity"] = (
    scal_global[["issue1", "issue2", "issue3"]].apply(lambda r: any(x in (5, 6) for x in r if pd.notna(x)), axis=1)
).astype(int)
scal_global["issue_rights"] = (
    scal_global[["issue1", "issue2", "issue3"]].apply(lambda r: any(x == 10 for x in r if pd.notna(x)), axis=1)
).astype(int)

# Repression checks
if "repress" in scal_global.columns:
    scal_global["flag_inconsistent_lethal_repress"] = (
        (scal_global["repress"] == 2) & (scal_global["ndeath_clean"].fillna(0) <= 0)
    ).astype(int)

# Simple actor/target buckets (heuristics)

def normalize_text(x):
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip().lower()


def bucket_actor_target(name: str) -> str:
    n = normalize_text(name)
    if n == "":
        return "Unknown"
    if any(k in n for k in ["police", "soldier", "military", "army", "security forces", "gendarmerie"]):
        return "State Security"
    if any(k in n for k in ["government", "ministry", "president", "governor", "mayor", "parliament"]):
        return "Government/State"
    if any(k in n for k in ["cartel", "gang", "drug", "sicario", "kidnap", "criminal"]):
        return "Criminal/Organized Crime"
    if any(k in n for k in ["gunmen", "assailants", "attackers", "armed men", "unknown gunmen", "mob"]):
        return "Generic Violent Actor"
    if any(k in n for k in ["party", "supporters", "campaign", "candidate"]):
        return "Political/Party"
    if any(k in n for k in ["ngo", "activist", "human rights", "union", "workers", "teachers", "students"]):
        return "Civil Society/Labor/Education"
    if any(k in n for k in ["citizen", "civilian", "villager", "protester", "demonstrator", "bystander"]):
        return "Civilians/Public"
    if any(k in n for k in ["muslim", "christian", "catholic", "hutu", "tutsi", "ethnic"]):
        return "Ethnic/Religious"
    if any(k in n for k in ["united nations", "world bank", "embassy", "ambassador", "foreign"]):
        return "International/Foreign"
    return "Other/Unclassified"

for col in ["actor1", "actor2", "actor3"]:
    if col in scal_global.columns:
        scal_global[f"{col}_bucket"] = scal_global[col].apply(bucket_actor_target)

for col in ["target1", "target2"]:
    if col in scal_global.columns:
        scal_global[f"{col}_bucket"] = scal_global[col].apply(bucket_actor_target)

scal_global["pattern_state_vs_civilians"] = (
    (scal_global.get("actor1_bucket", "Unknown") == "State Security")
    & (scal_global.get("target1_bucket", "Unknown") == "Civilians/Public")
).astype(int)

scal_global["pattern_nonstate_vs_gov"] = (
    (~scal_global.get("actor1_bucket", pd.Series("")).isin(["Government/State", "State Security"]))
    & (scal_global.get("target1_bucket", pd.Series("")) == "Government/State")
).astype(int)

# === Final dataset check ===
print("Final shape:", scal_global.shape)
print("\nFinal columns:")
print(scal_global.columns.tolist())

# --- Missing values ---
missing_summary = scal_global.isna().mean().sort_values(ascending=False).head(20)
print("\nTop 20 columns with missing values (fraction):")
print(missing_summary)

# --- Quick overview ---
print("\nSample rows after feature engineering:")
print(scal_global.head(5))

# --- Check consistency of key engineered variables ---
check_cols = [
    "etype_label",
    "etype_family",
    "issue_main",
    "ndeath_clean",
    "violent_event",
    "mass_casualty",
    "npart_clean",
    "mass_participation",
    "repression_level",
    "repression_event",
    "actor1_bucket",
    "target1_bucket",
    "pattern_state_vs_civilians",
    "pattern_nonstate_vs_gov",
]
print("\nSummary of engineered features:")
print(scal_global[check_cols].describe(include="all").transpose())

# --- Any remaining NaNs in key engineered variables? ---
print("\nRemaining NaNs in engineered features:")
print(scal_global[check_cols].isna().sum())

# --- 1) Identify low-information columns to drop ---
empty_cols = scal_global.columns[scal_global.isna().all()].tolist()
missing_ratio = scal_global.isna().mean()
high_missing_cols = missing_ratio[missing_ratio >= 0.80].index.tolist()
constant_cols = [c for c in scal_global.columns if scal_global[c].nunique(dropna=False) <= 1]
cols_to_drop = sorted(set(empty_cols) | set(high_missing_cols) | set(constant_cols))
explicit_keep = {}
cols_to_drop = [c for c in cols_to_drop if c not in explicit_keep]
print("Columns to drop (low information):")
print(cols_to_drop)

# Drop columns
scal_global = scal_global.drop(columns=cols_to_drop, errors="ignore").copy()

# --- 2) Impute npart_clean missing as 0 = "missing info" ---
if "npart_clean" not in scal_global.columns and "npart" in scal_global.columns:
    scal_global["npart_clean"] = scal_global["npart"].replace({-99: np.nan, -88: np.nan, -77: np.nan})
scal_global["npart_missing_flag"] = scal_global["npart_clean"].isna().astype(int)
scal_global["npart_clean"] = pd.to_numeric(scal_global["npart_clean"], errors="coerce").fillna(0).astype("Int64")
scal_global["mass_participation"] = (scal_global["npart_clean"].fillna(0) >= 4).astype(int)

# --- 3) Quick checks ---
print("\nShape after dropping low-information columns:", scal_global.shape)
print("\nTop remaining missingness:")
print(scal_global.isna().mean().sort_values(ascending=False).head(15))

print("\n`npart_clean` value counts (0 means 'missing info'):")
print(scal_global["npart_clean"].value_counts(dropna=False).sort_index())

# --- Save final artifact ---
scal_global.to_csv("scal_global_features_clean.csv", index=False)
# scal_global.to_parquet("scal_global_features_clean.parquet", index=False)
