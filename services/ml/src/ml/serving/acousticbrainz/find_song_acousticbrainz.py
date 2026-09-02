import json
from pathlib import Path


def get_acousticbrainz_data(mbid: str, base_extract_dir: Path) -> dict:
    song_data = {
        "highlevel": None,
        "lowlevel": None
    }

    # only -0 version
    target_filename = f"{mbid}-0.json"

    # Define exact file paths for both High-Level and Low-Level
    highlevel_file = (
            base_extract_dir
            / "acousticbrainz-highlevel-json-20220623"
            / "highlevel"
            / mbid[:2]
            / mbid[2]
            / target_filename
    )

    lowlevel_file = (
            base_extract_dir
            / "acousticbrainz-lowlevel-features-20220623"
            / "lowlevel"
            / mbid[:2]
            / mbid[2]
            / target_filename
    )

    # Load High-Level data
    if highlevel_file.exists():
        try:
            with open(highlevel_file, "r", encoding="utf-8") as f:
                song_data["highlevel"] = json.load(f)
        except Exception as e:
            print(f"Error reading high-level file {highlevel_file.name}: {e}")
    else:
        print(f"High-level file not found: {highlevel_file}")

    # Load Low-Level data
    if lowlevel_file.exists():
        try:
            with open(lowlevel_file, "r", encoding="utf-8") as f:
                song_data["lowlevel"] = json.load(f)
        except Exception as e:
            print(f"Error reading low-level file {lowlevel_file.name}: {e}")
    else:
        print(f"Low-level file not found: {lowlevel_file}")

    return song_data


# --- Example Usage ---
if __name__ == "__main__":
    extract_dir = Path(__file__).parent / "download_scripts" / "acousticbrainz-extracted"
    test_mbid = "1a0a0ac2-b294-4794-b275-1b064b31b3d5"

    song_data = get_acousticbrainz_data(test_mbid, extract_dir)

    if song_data["highlevel"]:
        print("--- HIGH-LEVEL DATA ---")

        file_data = song_data["highlevel"]

        metadata = file_data.get("metadata", {})
        tags = metadata.get("tags", {})

        title = tags.get("title", ["Unknown"])[0]
        artist = tags.get("artist", ["Unknown"])[0]

        features = file_data.get("highlevel", {})

        genre_data = features.get("genre_dortmund", {})
        genre = genre_data.get("value", "Unknown")

        print("\n--- QUICK SUMMARY ---")
        print(f"Title: {title}")
        print(f"Artist: {artist}")
        print(f"Predicted Genre: {genre}")