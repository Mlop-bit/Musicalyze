import requests


def search_deezer_track(isrc: str = None, artist: str = None, track: str = None, query: str = None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    if isrc:
        url_isrc = f"https://api.deezer.com/2.0/track/isrc:{isrc}"
        res = requests.get(url_isrc, headers=headers).json()
        if "error" not in res and res.get("id"):
            return format_response(res, "ISRC Search", headers)

    search_query = ""
    if artist and track:
        search_query = f'artist:"{artist}" track:"{track}"'
    elif artist:
        search_query = f'artist:"{artist}"'
    elif track:
        search_query = f'track:"{track}"'
    elif query:
        search_query = query

    if search_query:
        url_search = f"https://api.deezer.com/search?q={search_query}"
        res = requests.get(url_search, headers=headers).json()
        if res.get("data") and len(res["data"]) > 0:
            top_result = res["data"][0]
            track_details = requests.get(f"https://api.deezer.com/track/{top_result['id']}", headers=headers).json()
            return format_response(track_details, f"Flexible Search ('{search_query}')", headers)

    return None


def format_response(data: dict, method: str, headers: dict):
    album_id = data.get("album", {}).get("id")
    genres = []
    if album_id:
        album_res = requests.get(f"https://api.deezer.com/album/{album_id}", headers=headers).json()
        if "genres" in album_res and "data" in album_res["genres"]:
            genres = [g["name"] for g in album_res["genres"]["data"]]

    return {
        "method": method,
        "deezer_id": data.get("id"),
        "isrc": data.get("isrc"),
        "title": data.get("title"),
        "artist": data.get("artist", {}).get("name"),
        "bpm": data.get("bpm"), # si 0, alors pas donné lors de la publication ou un truc comme ça
        "duration_sec": data.get("duration"),
        "release_date": data.get("release_date"),
        "popularity_rank": data.get("rank"), #ranking de popularité deezer 1m est le max, et est la meilleur note possible
        "explicit_lyrics": data.get("explicit_lyrics"),
        "gain_db": data.get("gain"), #gain en DB pour la normalisation audio entre les sons je crois
        "genres": genres,
        "preview_url": data.get("preview") #marche presque pas malheuresement
    }


# --- TESTS ---

test_1 = search_deezer_track(track="Get Lucky")             #le premier titre trouvé correspondant à ce titre, mais ce n'est pas forcément celui que l'on veut
test_2 = search_deezer_track(artist="Daft Punk")             #daft punk est dans les crédits de ce titre après vérification, donc pas d'erreurs
test_3 = search_deezer_track(query="Daft Punk Get Lucky")   #bonne précision de recherche /!\ATTENTION/!\ l'odre pourrait peut-être influer, essayons de garder l'artiste en premier
test_4 = search_deezer_track(isrc="GB28K1100036")           # meilleure recherche possible, par ISRC donc

for i, result in enumerate([test_1, test_2, test_3, test_4], 1):
    if result:
        print(f"\n--- Test {i} Success ---")
        for key, value in result.items():
            print(f"{key:<20}: {value}") # {key:<20} est juste là pour l'allignement d'affichage en fonction de la key
        print("\n")
    else:
        print(f"\n--- Test {i} Failed ---")