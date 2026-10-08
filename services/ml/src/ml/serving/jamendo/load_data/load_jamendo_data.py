import os

from pydantic import HttpUrl, SecretStr

from ml.core.config import Settings
from ml.serving.jamendo.jamendo_dataset import JamendoDataset
from ml.serving.jamendo.load_data.load_jamendo_dataset import load_jamendo_dataset
from ml.serving.jamendo.load_data.load_jamendo_embeddings import load_jamendo_embeddings


def load_jamendo_data(settings: Settings) -> JamendoDataset:
    moodtheme_train_file_path = "../data/mtg-jamendo/split-0/autotagging_moodtheme-train.tsv"
    moodtheme_file_path = "../data/mtg-jamendo/autotagging_moodtheme.tsv"
    train_files_path = "../data/mtg-jamendo/mp3s/"

    jamendo_dataset = load_jamendo_dataset(moodtheme_train_file_path, moodtheme_file_path, settings)
    load_jamendo_embeddings(train_files_path, jamendo_dataset, settings)

    return jamendo_dataset


if __name__ == "__main__":
    settings = Settings(
        s3_endpoint_url=HttpUrl(os.environ["MUSICALYZE_S3_ENDPOINT_URL"]),
        s3_region=os.environ["MUSICALYZE_S3_REGION"],
        s3_bucket=os.environ["MUSICALYZE_S3_BUCKET"],
        s3_access_key=os.environ["MUSICALYZE_S3_ACCESS_KEY"],
        s3_secret_key=SecretStr(os.environ["MUSICALYZE_S3_SECRET_KEY"]),
        kv_account_id=os.environ["MUSICALYZE_KV_ACCOUNT_ID"],
        kv_namespace_id=os.environ["MUSICALYZE_KV_NAMESPACE_ID"],
        kv_api_token=SecretStr(os.environ["MUSICALYZE_KV_API_TOKEN"]),
        db_host=os.environ["DB_HOST"],
        db_port=int(os.environ["DB_PORT"]),
        db_user=os.environ["DB_USER"],
        db_password=SecretStr(os.environ["DB_PASSWORD"]),
        db_name=os.environ["DB_NAME"],
    )

    load_jamendo_data(settings)
