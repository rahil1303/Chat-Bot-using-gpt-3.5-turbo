import pandas as pd


facts_df = pd.read_excel('Rohit_Sharma_Facts.xlsx')

print(facts_df.head())

facts_df = pd.read_excel('Rohit_Sharma_Facts.xlsx')
facts_list = facts_df['Fact'].tolist()

def get_rohit_fact(fact_number):
    """Returns a fact about Rohit Sharma based on the fact number."""
    if 1 <= fact_number <= len(facts_list):
        return facts_list[fact_number - 1]
    else:
        return "I don't have that many facts about Rohit Sharma."

def get_random_fact():
    """Returns a random fact about Rohit Sharma."""
    import random
    return random.choice(facts_list)
