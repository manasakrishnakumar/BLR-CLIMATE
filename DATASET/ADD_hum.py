import pandas as pd

# Load dataset
df = pd.read_csv("dataset.csv")

# Convert Date column
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')

# Convert temperature columns to numeric
df['Temp Max'] = pd.to_numeric(df['Temp Max'], errors='coerce')
df['Temp Min'] = pd.to_numeric(df['Temp Min'], errors='coerce')

# Estimate Humidity
# Formula:
# Humidity = 100 - 2 * (Temp Max - Temp Min)

df['Humidity'] = 100 - 2 * (df['Temp Max'] - df['Temp Min'])

# Keep values between 0 and 100
df['Humidity'] = df['Humidity'].clip(0, 100)

# Round values
df['Humidity'] = df['Humidity'].round(2)

# Save new file
df.to_csv("data.csv", index=False)

print("Saved successfully as data.csv")
print(df.head())