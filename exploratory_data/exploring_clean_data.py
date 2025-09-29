import pandas as pd

#  =========================================================================
#                       1.  GENERAL
#  =========================================================================

df = pd.read_csv("C:/Users/diego/OneDrive/Escritorio/Proyecto Scad/exploratory_data/scal_global_features_clean.csv")

print(df.head())

print("\nColumnas:")
print(df.columns.tolist())

print("\nValores nulos por columna:")
print(df.isnull().sum())



#  =========================================================================
#                       2.  CATEGORICAS
#  =========================================================================


# Filtrar columnas categóricas
categorical_cols = df.select_dtypes(include='object').columns

# Mostrar valores únicos por columna categórica
for col in categorical_cols:
    print(f" {col}")
    print(f"   Número de categorías: {df[col].nunique()}")
    print(f"   Categorías: {df[col].unique()[:10]}")  # Muestra solo las primeras 10 para no saturar
    print("-" * 60)

# Convertir todos los valores de esas columnas a minúsculas
for col in categorical_cols:
    df[col] = df[col].astype(str).str.lower()




#  =========================================================================
#                       3.  NUMERICAS
#  =========================================================================

# Seleccionar columnas numéricas
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

# Mostrar nombres de columnas numéricas
print(" Columnas numéricas:")
print(numeric_cols.tolist())

# Estadísticas descriptivas
print("\nEstadísticas básicas:")
print(df[numeric_cols].describe())

for col in numeric_cols:
    print(f" {col} — {df[col].nunique()} valores únicos")

for col in numeric_cols:
    print(f"{col}: valores mínimos y máximos")
    print(df[col].value_counts().head(10))  # Muestra los más frecuentes
    print("-" * 40)

import matplotlib.pyplot as plt

df['duration_days'].hist(bins=50)
plt.title("Distribución de duración de eventos")
plt.xlabel("Días")
plt.ylabel("Frecuencia")
plt.show()

# Limpiar columnas numéricas
# Reemplazar valores codificados como -99 o "missing"
replace_dict = {
    -99: pd.NA,
    "missing": pd.NA,
    "Missing": pd.NA
}
df.replace(replace_dict, inplace=True)

# Eliminar el evento con eventid -5300001.0
df = df[df['eventid'] != -5300001.0]

# Eliminar columnas completamente vacías (opcional)
df.dropna(axis=1, how='all', inplace=True)

# Eliminar filas completamente vacías (opcional)
df.dropna(axis=0, how='all', inplace=True)

# --- Normalización de categorías específicas ---

# Quitar espacios en blanco en extremos
for col in categorical_cols:
    df[col] = df[col].str.strip()

# Normalización de nombres de países
if "countryname" in df.columns:
    country_fix = {
        "democratic republic of the congo": "democratic republic of congo"
    }
    df["countryname"] = df["countryname"].replace(country_fix)


# Guardar el nuevo CSV limpio
df.to_csv("scad_final_dataset.csv", index=False)
