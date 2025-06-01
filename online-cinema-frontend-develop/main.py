import requests

url = "https://api.themoviedb.org/3/authentication/token/new"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NTc1OTEzZGNhYWZkYjFlZmQ1N2ZiZWZhNWE3NzNjZiIsIm5iZiI6MTczMjIxNDQyNS4zNDQsInN1YiI6IjY3M2Y3ZTk5ODcwODFjNzI1YTk3MjgwZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.suRKgHJCd6423Ol2JgXhJEP3Wog-FrY_KQQuPF3tRNU"
}

# 1. Сначала попробуйте без прокси, чтобы проверить прямое соединение
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Произошла ошибка при запросе: {str(e)}")
    print(f"Тип ошибки: {type(e).__name__}")

# 2. Если нужен прокси, убедитесь, что указаны правильные данные
proxies = {
    'http': 'http://username:password@proxy-host:port',
    'https': 'https://username:password@proxy-host:port'
}