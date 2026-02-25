# MovieSubsMaker CLI 🎬

Local, open-source CLI tool for generating high-quality subtitles using AI. It handles transcription, translation, and automated timing synchronization.

## ✨ Features
* **Full Pipeline (`full`)**: Transcribes video audio and translates it to the target language in one go.
* **Smart Translation (`translate`)**: Translates existing `.srt` files locally without hitting external APIs.
* **Timing Synchronization (`sync`)**: Automatically aligns out-of-sync subtitles to the video's audio track using `ffsubsync`.
* **Anime Support**: Built-in support for the `litagin/anime-whisper` domain model for superior Japanese transcription.
* **Auto Hardware Detection**: Seamlessly switches between CPU, Apple Silicon (MPS), and GPU (CUDA) for maximum performance.
* **Cache Management (`clean`)**: Easily free up disk space by removing heavy AI models with a single command.

## 🛠️ Tech Stack
* **Python** (Core CLI logic + `argparse`)
* **stable-ts** (Audio transcription & precise timestamping via Whisper)
* **Transformers & Torch** (Translation via NLLB-200)
* **ffsubsync** (Audio-based subtitle synchronization)
* **Rich** (Beautiful terminal outputs)

## 🚀 Installation

### 1. Install system dependencies
Make sure you have `ffmpeg` installed on your system, as it's required for audio extraction.
* **Linux (Ubuntu/Mint):** `sudo apt update && sudo apt install ffmpeg`
* **macOS:** `brew install ffmpeg`
* **Windows:** Download via winget: `winget install ffmpeg` or from the [official site](https://ffmpeg.org/download.html).

### 2. Clone the repo & set up the environment
```bash
git clone https://github.com/xSerj111/MovieSubsMaker.git
cd MovieSubsMaker
python -m venv venv
```

### 3. Activate the virtual environment
* **Linux / macOS:** 
```bash
source venv/bin/activate
```

* **Windows (Command Prompt):** 
```cmd
venv\Scripts\activate
```

> **Note for Windows PowerShell users:** If you get an "Execution of scripts is disabled" error, run Windows PowerShell as Administrator and execute: `Set-ExecutionPolicy Unrestricted -Force`, then try activating again.

### 4. Install Python packages
```bash
pip install -r requirements.txt
```

> ⚠️ **IMPORTANT: NVIDIA GPU Users (Windows/Linux)** > To unleash maximum performance and hardware acceleration, install the CUDA version of PyTorch instead of the default one:
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
> ```

---

## 📖 Usage Examples

**1. Generate Polish subtitles from an English video:**
```bash
python main.py full movie.mp4 --target-lang pl
```

**2. Generate English subtitles for a Japanese Anime (using domain-specific model):**
```bash
python main.py full episode.mkv --source-lang ja --target-lang en --anime
```

**3. Translate an existing SRT file (e.g. Japanese to Polish):**
```bash
python main.py translate subs.srt --source-lang ja --target-lang pl
```

**4. Synchronize out-of-sync subtitles to a video:**
```bash
python main.py sync movie.mp4 out_of_sync_subs.srt
```

**5. Clean up downloaded AI models from disk:**
```bash
python main.py clean
```

## 📋 Roadmap
- [x] Audio Transcription (Stable-ts / Whisper)
- [x] Subtitle Translation (NLLB-200)
- [x] Cache Management
- [x] Subtitle Synchronization (`ffsubsync`)
- [ ] Context-aware subtitle translation (Sentence merging)
