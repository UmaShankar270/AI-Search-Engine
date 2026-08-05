import requests


def search_repositories(
    query: str,
    language: str = None,
    page: int = 1,
    per_page: int = 10
):
    if language:
        query = f"{query} language:{language}"

    url = "https://api.github.com/search/repositories"

    response = requests.get(
        url,
        params={
            "q": query,
            "page": page,
            "per_page": per_page
        },
        timeout=10
    )

    data = response.json()

    repos = []

    for repo in data.get("items", []):
        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "language": repo["language"],
            "url": repo["html_url"]
        })

    return repos