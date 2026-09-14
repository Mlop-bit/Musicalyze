import librosa
import torch
from ml.core.muq import embed, load_model

model = load_model()

audio_np, sample_rate = librosa.load("7400.low.mp3", sr=None)

waveform = torch.from_numpy(audio_np).unsqueeze(0)

embedding = embed(model, waveform)
print("Embedding :", embedding.shape)