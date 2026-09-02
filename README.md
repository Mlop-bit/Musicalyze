# Musicalyze

## Problem statement
??

## Background
The ubiquity of streaming music has led users to accumulate extensive, unstructured track libraries. These collections typically lack stylistic coherence and optimal sequencing, complicating both playlist curation and targeted music discovery. This challenge is currently exacerbated by API restrictions: as of November 2024, Spotify deprecated the endpoints providing acoustic features (e.g., tempo, energy, key) and algorithmic recommendations for new applications. Consequently, external applications can no longer rely on native platform metadata for audio analysis.
This project proposes a Spotify-integrated web application that independently reconstructs this acoustic metadata to circumvent current API limitations. The architecture combines an open-source pretrained music model (MuQ) with public datasets (AcousticBrainz, MTG-Jamendo), Leveraging this consolidated data, the application automatically segments playlists into mood-coherent subsets, computes optimal track sequences, and generates targeted recommendations. These functions are driven by a custom-trained mood and genre classifier, establishing a self-sufficient Music Information Retrieval (MIR) pipeline independent of proprietary third-party services.
Specifications
Has to run on any recent browser. 

## Objectives
- Build an independent data pipeline to reconstruct missing acoustic metadata using a combination of public music datasets and a pretrained model
- Train and evaluate a custom mood and genre classifier using these reconstructed acoustic representations.
- Develop a web application that applies the classification outputs to automate playlist segmentation, track sequencing, and music recommendation.

## Specification
- Has to run on any recent browser.
- ?

## Prerequisites
??

## Installation
To install this project, simply clone the repository using the following command:
```
https://github.com/Mlop-bit/AIProject.git
```

## Project initialisation
1. Create a `.env` file in the project’s `services/ml/` folder.
2. Please enter the following variables :

| Variable                     | Description |
| ---------------------------- | ----------- |
| `MUSICALYZE_S3_ENDPOINT_URL` |             |
| `MUSICALYZE_S3_REGION`       |             |
| `MUSICALYZE_S3_BUCKET`       |             |
| `MUSICALYZE_S3_ACCESS_KEY`   |             |
| `MUSICALYZE_S3_SECRET_KEY`   |             |
| `MUSICALYZE_KV_ACCOUNT_ID`   |             |
| `MUSICALYZE_KV_NAMESPACE_ID` |             |
| `MUSICALYZE_KV_API_TOKEN`    |             |

## Project launch
??