"""
Deep analysis of diabetes dataset to understand why it's performing at 50%
"""
import pandas as pd
import numpy as np

df = pd.read_csv('data/diabetes_prediction_india (1).csv')

print("=" * 70)
print("DIABETES DATASET ANALYSIS")
print("=" * 70)

# Basic info
print(f"\nShape: {df.shape}")
print(f"\nTarget distribution:")
print(df['Diabetes_Status'].value_counts())
print(f"\nTarget percentage:")
print(df['Diabetes_Status'].value_counts(normalize=True))

# Check for data quality issues
print("\n" + "=" * 70)
print("DATA QUALITY CHECKS")
print("=" * 70)

# Check if features have any predictive power
print("\nNumeric features correlation with target:")
df_encoded = df.copy()
df_encoded['Diabetes_Status'] = (df_encoded['Diabetes_Status'] == 'Yes').astype(int)

numeric_cols = df_encoded.select_dtypes(include=[np.number]).columns
correlations = df_encoded[numeric_cols].corr()['Diabetes_Status'].sort_values(ascending=False)
print(correlations)

# Check categorical features
print("\n" + "=" * 70)
print("CATEGORICAL FEATURES VS TARGET")
print("=" * 70)

categorical_cols = ['Gender', 'Family_History', 'Physical_Activity', 'Diet_Type', 
                   'Smoking_Status', 'Stress_Level', 'Hypertension']

for col in categorical_cols:
    if col in df.columns:
        print(f"\n{col}:")
        ct = pd.crosstab(df[col], df['Diabetes_Status'], normalize='index')
        print(ct)

# Check for duplicate or constant features
print("\n" + "=" * 70)
print("FEATURE VARIANCE")
print("=" * 70)
print("\nNumeric features with low variance:")
for col in numeric_cols:
    if col != 'Diabetes_Status':
        variance = df_encoded[col].var()
        if variance < 0.1:
            print(f"  {col}: variance = {variance:.4f}")

# Sample some rows
print("\n" + "=" * 70)
print("SAMPLE DATA")
print("=" * 70)
print(df.head(20))
