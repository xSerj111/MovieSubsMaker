import stable_whisper
import torch
from pathlib import Path
from rich.console import Console
from transformers import pipeline  # <--- Nowy import! Użyjemy go do ominięcia błędu

console = Console()

def run(video_path: Path, model_name: str = "small", source_lang: str = None, use_anime_model: bool = False) -> Path:
    # 1. Detekcja sprzętu
    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"Compute device: [highlight]{device.upper()}[/highlight]")
    console.print("Loading model into memory...")

    # 2. Wybór i ładowanie modelu (Ręczny Bypass Błędu)
    if use_anime_model:
        actual_model = "litagin/anime-whisper"
        console.print(f"Loading domain model directly via Transformers pipeline: [highlight]{actual_model}[/highlight]")
        
        # OMIJAMY BŁĄD W STABLE-TS: Tworzymy rurociąg (pipeline) ręcznie,
        # pomijając zepsute argumenty z 'use_flash_attention_2'.
        pipe = pipeline(
            "automatic-speech-recognition",
            model=actual_model,
            device=device,
            chunk_length_s=30  # Zabezpiecza pamięć RAM przed przepełnieniem
        )
        
        # Podajemy gotowy pipeline do stable-ts
        model = stable_whisper.load_hf_whisper(actual_model, pipeline=pipe)
    else:
        actual_model = model_name
        model = stable_whisper.load_model(actual_model, device=device)

    # 3. Rozpoczęcie transkrypcji
    console.print(f"[info]Starting transcription for: {video_path.name}[/info]")
    
    transcribe_kwargs = {"vad": True}
    if source_lang:
        transcribe_kwargs["language"] = source_lang
        console.print(f"[info]Forced source language: {source_lang}[/info]")
    
    result = model.transcribe(str(video_path), **transcribe_kwargs)
    
    # 4. Zapis do pliku SRT
    output_srt = video_path.with_suffix(".srt")
    result.to_srt_vtt(str(output_srt))
    
    console.print(f"[success]Transcription finished! Saved as: {output_srt.name}[/success]")
    return output_srt
