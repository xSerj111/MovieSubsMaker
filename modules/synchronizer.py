import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

def run(video_path: Path, srt_path: Path, output_path: Path = None) -> Path:
    """
    Synchronizes an external SRT file to the audio track of a video using ffsubsync.
    """
    # If no output path is provided, create a default one
    if not output_path:
        output_path = srt_path.with_name(f"{srt_path.stem}_synced.srt")

    console.print(f"[info]Analyzing audio from '{video_path.name}' and aligning '{srt_path.name}'...[/info]")
    console.print("[warning]This might take a minute depending on the video length. Please wait...[/warning]")

    # Build the ffsubsync CLI command
    # Syntax: ffsubsync video.mp4 -i original.srt -o synced.srt
    command = [
        "ffsubsync",
        str(video_path),
        "-i", str(srt_path),
        "-o", str(output_path)
    ]

    try:
        # Run the command and capture errors if they happen
        subprocess.run(command, check=True, capture_output=True, text=True)
        console.print(f"[success]Synchronization successful! Saved as: {output_path.name}[/success]")
        return output_path
        
    except subprocess.CalledProcessError as e:
        console.print("[error]Synchronization failed![/error]")
        console.print(f"[error]Details: {e.stderr}[/error]")
        raise
    except FileNotFoundError:
        console.print("[error]ffsubsync command not found. Is it installed in your virtual environment?[/error]")
        raise
