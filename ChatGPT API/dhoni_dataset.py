import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

# Load the MS Dhoni facts dataset
ms_dhoni_df = pd.read_excel('MS_Dhoni_Facts.xlsx')

# Create training and testing datasets
X = ms_dhoni_df['Fact']  # The facts
y = ms_dhoni_df['Fact Number']  # Labels (fact numbers)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Create a pipeline with a TF-IDF vectorizer and a logistic regression classifier
model = make_pipeline(TfidfVectorizer(), LogisticRegression())

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Test the model with some sample queries
sample_queries = [
    "When did MS Dhoni retire from Test cricket?",
    "What is Dhoni's highest score in ODI?",
    "Which team did Dhoni captain in the IPL?"
]

for query in sample_queries:
    fact_number_pred = model.predict([query])[0]
    fact = ms_dhoni_df[ms_dhoni_df['Fact Number'] == fact_number_pred]['Fact'].values[0]
    print(f"Query: {query}")
    print(f"Predicted Fact: {fact}")
    print("-" * 50)

# Save the model for future use
import pickle
with open('ms_dhoni_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model training complete and saved as 'ms_dhoni_model.pkl'")
