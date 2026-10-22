import pandas as pd
import numpy as np

# =========================================================
# LOAD DATASET
# =========================================================

file_path = "data.csv"

print("\nLoading dataset...\n")

# Try normal CSV loading first
try:
    df = pd.read_csv(file_path)
    print("Dataset loaded successfully using default separator ','")
except Exception as e:
    print("Default loading failed:", e)

# =========================================================
# BASIC DATASET INFO
# =========================================================

print("\n================ DATASET SHAPE ================\n")
print(df.shape)

print("\n================ FIRST 5 ROWS ================\n")
print(df.head())

print("\n================ COLUMN NAMES ================\n")
print(df.columns.tolist())

print("\n================ DATA TYPES ================\n")
print(df.dtypes)

# =========================================================
# CHECK IF CSV PARSING FAILED
# =========================================================

if len(df.columns) == 1:
    print("\nWARNING:")
    print("Only ONE column detected.")
    print("CSV separator is probably wrong.")

    print("\nTrying semicolon separator ';'...\n")

    try:
        df = pd.read_csv(file_path, sep=';')

        print("\nDataset loaded using ';' separator")

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nFirst rows:")
        print(df.head())

    except Exception as e:
        print("Semicolon loading also failed:", e)

# =========================================================
# CHECK FOR OBJECT COLUMNS
# =========================================================

print("\n================ OBJECT COLUMNS ================\n")

object_cols = df.select_dtypes(include=['object']).columns

print(object_cols)

# =========================================================
# CHECK SAMPLE VALUES OF OBJECT COLUMNS
# =========================================================

for col in object_cols:
    print(f"\n----- SAMPLE VALUES FROM COLUMN: {col} -----\n")
    print(df[col].astype(str).head(10))

# =========================================================
# TRY CONVERTING NUMERIC COLUMNS
# =========================================================

print("\n================ CONVERTING POSSIBLE NUMERIC COLUMNS ================\n")

for col in df.columns:

    # Skip obvious text/date columns
    if col.lower() in ['date', 'month', 'year']:
        continue

    try:
        # Remove spaces
        df[col] = df[col].astype(str).str.strip()

        # Convert to numeric
        converted = pd.to_numeric(df[col], errors='coerce')

        # Check how many valid numeric values exist
        valid_count = converted.notna().sum()

        # If many values converted successfully, keep conversion
        if valid_count > len(df) * 0.5:
            df[col] = converted
            print(f"{col} --> Converted to numeric")

    except Exception as e:
        print(f"{col} --> Conversion failed")
        print(e)

# =========================================================
# FINAL DATA TYPES
# =========================================================

print("\n================ FINAL DATA TYPES ================\n")
print(df.dtypes)

# =========================================================
# CHECK MISSING VALUES
# =========================================================

print("\n================ MISSING VALUES ================\n")
print(df.isnull().sum())

# =========================================================
# REMOVE BAD ROWS
# =========================================================

numeric_cols = df.select_dtypes(include=[np.number]).columns

df_clean = df.dropna(subset=numeric_cols)

print("\n================ CLEANED DATASET SHAPE ================\n")
print(df_clean.shape)

# =========================================================
# TEST GROUPBY
# =========================================================

print("\n================ TESTING GROUPBY =================\n")

if 'Year' in df_clean.columns:

    for col in numeric_cols:

        if col != 'Year':

            try:
                yearly_mean = df_clean.groupby('Year')[col].mean()

                print(f"\nSUCCESS: Groupby mean worked for column -> {col}")

                print(yearly_mean.head())

            except Exception as e:

                print(f"\nFAILED: {col}")

                print(e)

else:
    print("No 'Year' column found.")

# =========================================================
# SAVE CLEANED DATASET
# =========================================================

output_file = "cleaned_dataset.csv"

df_clean.to_csv(output_file, index=False)

print(f"\nCleaned dataset saved as: {output_file}")

print("\n================ PROCESS COMPLETED ================\n")