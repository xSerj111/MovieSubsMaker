import argparse
import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.theme import Theme

# We import our transcriber and translator module
from modules import transcriber, translator, synchronizer

# Configure colors for console logs
custom_theme = Theme({
    "info": "cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "magenta"
})
console = Console(theme=custom_theme)

def handle_full_mode(args):
    console.print(f"Video: [highlight]{args.video}[/highlight]")
    console.print(f"Target language: [bold]{args.target_lang}[/bold]")
    if args.anime:
        console.print("Activated [highlight]ANIME[/highlight] profile (forced domain model).")
    else:
        console.print(f"STT Model: [bold]{args.model}[/bold]")
    
    console.print("\n[info]--- STAGE 1: TRANSCRIPTION ---[/info]")
    
    # Run the transcription module
    raw_srt_path = transcriber.run(
        video_path=args.video,
        model_name=args.model,
        use_anime_model=args.anime,
        source_lang=args.source_lang
    )

    console.print("\n[success]Stage 1 completed successfully![/success]")
    
    console.print("\n[info]--- STAGE 2: TRANSLATION ---[/info]")
    
    final_srt_path = translator.run(
        srt_path=raw_srt_path,
        source_lang=args.source_lang,
        target_lang=args.target_lang
    )
    
    console.print(f"\n[success]All done! Your final file is ready: {final_srt_path.name}[/success]")


def handle_translate_mode(args):
    console.print(f"Subtitles (source): [highlight]{args.srt}[/highlight]")
    console.print(f"Target language: [bold]{args.target_lang}[/bold]")
    
    console.print("\n[info]--- TRANSLATION ONLY ---[/info]")
    
    final_srt_path = translator.run(
        srt_path=args.srt,
        source_lang=args.source_lang,
        target_lang=args.target_lang
    )
    
    console.print(f"\n[success]Translation completed! File ready: {final_srt_path.name}[/success]")


def handle_clean_mode(args):
    console.print("\n[info]--- CACHE CLEANUP ---[/info]")
    home = Path.home()
    
    # We carefully target ONLY the models our app downloads
    targets = [
        home / ".cache" / "huggingface" / "hub" / "models--facebook--nllb-200-distilled-600M",
        home / ".cache" / "huggingface" / "hub" / "models--litagin--anime-whisper",
        home / ".cache" / "whisper"  # OpenAI models (turbo, small, etc.)
    ]
    
    total_freed = 0
    for target in targets:
        if target.exists() and target.is_dir():
            # Calculate folder size
            size_bytes = sum(f.stat().st_size for f in target.rglob('*') if f.is_file())
            total_freed += size_bytes
            
            # Remove the folder securely
            shutil.rmtree(target)
            console.print(f"[success]Deleted:[/success] {target.name} ({size_bytes / (1024**3):.2f} GB)")
        else:
            console.print(f"[warning]Not found (already clean):[/warning] {target.name}")
            
    if total_freed > 0:
        console.print(f"\n[success]Cleanup complete! Freed up {total_freed / (1024**3):.2f} GB of disk space.[/success]")
    else:
        console.print("\n[info]Nothing to clean. Disk is already tidy![/info]")


def handle_sync_mode(args):
    console.print(f"Video: [highlight]{args.video}[/highlight]")
    console.print(f"Subtitles (source): [highlight]{args.srt}[/highlight]")
    
    console.print("\n[info]--- TIMING SYNCHRONIZATION ---[/info]")
    
    try:
        final_srt_path = synchronizer.run(
            video_path=args.video,
            srt_path=args.srt,
            output_path=args.output
        )
        console.print(f"\n[success]All done! Synced file is ready: {final_srt_path.name}[/success]")
    except Exception as e:
        console.print("\n[error]Synchronization process encountered an error and stopped.[/error]")
        sys.exit(1)


def main():
    examples = """
Examples of usage:
  # 1. Full pipeline (auto-detect source, translate to Polish)
  python main.py full video.mp4

  # 2. Full pipeline for anime (Japanese to English) using domain model
  python main.py full anime_episode.mkv --source-lang ja --target-lang en --anime

  # 3. Translate an existing SRT file directly
  python main.py translate subtitles.srt --source-lang ja --target-lang pl

  # 4. Sync existing subtitles to a video
  python main.py sync video.mp4 subs.srt
    """
    
    parser = argparse.ArgumentParser(
        description="Subtitle Creator CLI - Local tool for subtitle generation and synchronization.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Select operation mode", required=True)

    # --- FULL MODE ---
    parser_full = subparsers.add_parser("full", help="Full pipeline: Transcription -> Translation")
    parser_full.add_argument("video", type=Path, help="Path to the video file")
    parser_full.add_argument("--source-lang", type=str, help="Source language (e.g., 'ja', 'en'). Omit for auto-detect.")
    parser_full.add_argument("--target-lang", type=str, default="pl", help="Target translation language (default: 'pl')")
    parser_full.add_argument("--model", type=str, default="small", help="Whisper model size (default: 'small')")
    parser_full.add_argument("--anime", action="store_true", help="Use 'litagin/anime-whisper' model optimized for Japanese anime")
    parser_full.add_argument("--output", type=Path, help="Path to save the output file (optional)")

    # --- TRANSLATE MODE (NEW) ---
    parser_translate = subparsers.add_parser("translate", help="Translate only: Translate an existing SRT file")
    parser_translate.add_argument("srt", type=Path, help="Path to the SRT file")
    parser_translate.add_argument("--source-lang", type=str, help="Source language (e.g., 'ja', 'en')")
    parser_translate.add_argument("--target-lang", type=str, default="pl", help="Target translation language")

    # --- SYNC MODE ---
    parser_sync = subparsers.add_parser("sync", help="Sync only: Adjust existing SRT to video audio")
    parser_sync.add_argument("video", type=Path, help="Path to the video file")
    parser_sync.add_argument("srt", type=Path, help="Path to the original SRT file")
    parser_sync.add_argument("--output", type=Path, help="Path to save the synchronized SRT file (optional)")

    # --- CLEAN MODE (NEW) ---
    parser_clean = subparsers.add_parser("clean", help="Remove downloaded AI models to free up disk space")

    args = parser.parse_args()

    # Validate paths
    if hasattr(args, 'video') and args.video and not args.video.exists():
        console.print(f"[error]Error: Video file '{args.video}' does not exist.[/error]")
        sys.exit(1)
        
    if hasattr(args, 'srt') and args.srt and not args.srt.exists():
        console.print(f"[error]Error: Subtitle file '{args.srt}' does not exist.[/error]")
        sys.exit(1)

    # App header
    console.rule("[bold blue]Subtitle Creator CLI")
    
    # Run the appropriate mode
    if args.mode == "full":
        console.print("[info]Running mode:[/info] [bold]FULL[/bold]")
        handle_full_mode(args)
    elif args.mode == "translate":
        console.print("[info]Running mode:[/info] [bold]TRANSLATE[/bold]")
        handle_translate_mode(args)
    elif args.mode == "sync":
        console.print("[info]Running mode:[/info] [bold]SYNC[/bold]")
        handle_sync_mode(args)
    elif args.mode == "clean":  # <--- NEW CONDITION
        console.print("[info]Running mode:[/info] [bold]CLEAN[/bold]")
        handle_clean_mode(args)

if __name__ == "__main__":
    main()
