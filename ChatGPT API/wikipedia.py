import requests

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{query}"

def get_wikipedia_summary(query):
    summary_url = WIKI_SUMMARY_URL.format(query=query.replace(' ', '_'))
    response = requests.get(summary_url)
    data = response.json()
    if "extract" in data:
        return data['extract']
    else:
        return None
