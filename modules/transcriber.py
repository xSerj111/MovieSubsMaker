import stable_whisper
import torch
from pathlib import Path
from rich.console import Console

console = Console()

def run(video_path: Path, model_name: str = "small", use_anime_model: bool = False, source_lang: str = None) -> Path:
    """
    Runs video transcription using stable-ts.
    Returns the path to the generated SRT file.
    """
    # 1. Automatic hardware detection
    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"[info]Compute device:[/info] [bold]{device.upper()}[/bold]")

    # 2. Model selection and loading
    console.print("[info]Loading model into memory (it will be downloaded on the first run)...[/info]")
    
    if use_anime_model:
        actual_model = "litagin/anime-whisper"
        console.print(f"[info]Loading domain model from HuggingFace:[/info] [highlight]{actual_model}[/highlight]")
        # This specific function handles non-standard HuggingFace models
        model = stable_whisper.load_hf_whisper(actual_model, device=device)
    else:
        actual_model = model_name
        console.print(f"[info]Loading standard Whisper model:[/info] [highlight]{actual_model}[/highlight]")
        # This handles standard OpenAI models (small, medium, turbo, etc.)
        model = stable_whisper.load_model(actual_model, device=device)

    console.print(f"[warning]Starting audio transcription for '{video_path.name}'. This might take a while on a CPU![/warning]")

    # 3. Actual transcription
    result = model.transcribe(
        str(video_path),
        language=source_lang,
        word_timestamps=True,
        vad=True 
    )

    # 4. Save result to SRT file
    output_srt_path = video_path.with_suffix(".srt")
    
    result.to_srt_vtt(str(output_srt_path), word_level=False)

    console.print(f"[success]Transcription successful! Saved as:[/success] {output_srt_path.name}")
    
    return output_srt_path
