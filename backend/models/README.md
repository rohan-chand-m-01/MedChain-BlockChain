# Random Forest Models

Place your trained .pkl files here:

- `medichain_diabetes_model.pkl` - Diabetes risk prediction (UCI Pima dataset, ~77% accuracy)
- `medichain_heart_model.pkl` - Heart disease prediction (UCI Heart dataset, ~83% accuracy)  
- `medichain_kidney_model.pkl` - Kidney disease prediction (UCI CKD dataset, ~92% accuracy)

## Expected .pkl structure

Each pickle file should contain a dict:
```python
{
    "model": trained_sklearn_model,  # RandomForestClassifier
    "features": ["feature1", "feature2", ...],  # Feature names in order
    "accuracy": 0.77  # Test accuracy
}
```

## Training in Colab

Run cells 8-13 in your Colab notebook to train all three models, then download the .pkl files and place them here.

If models are missing, the system will return a default risk_score of 50 with a note.
