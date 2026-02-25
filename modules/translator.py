import pysrt
import torch
from pathlib import Path
from rich.console import Console
from rich.progress import track
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

console = Console()

# NLLB uses specific BCP-47 language codes instead of simple ISO codes
NLLB_LANG_MAP = {
    "pl": "pol_Latn",
    "en": "eng_Latn",
    "ja": "jpn_Jpan",
    "es": "spa_Latn",
    "de": "deu_Latn",
    "fr": "fra_Latn",
    "uk": "ukr_Cyrl",
    "it": "ita_Latn"
}

def get_nllb_code(iso_code: str) -> str:
    """Converts simple ISO codes (e.g. 'pl') to NLLB formats (e.g. 'pol_Latn')."""
    if not iso_code:
        console.print("[warning]No source language provided. Defaulting to English (eng_Latn) for translation.[/warning]")
        return "eng_Latn"
        
    code = NLLB_LANG_MAP.get(iso_code.lower())
    if not code:
        console.print(f"[warning]Warning: Language code '{iso_code}' not found in mapping. Defaulting to English.[/warning]")
        return "eng_Latn"
    return code

def run(srt_path: Path, source_lang: str, target_lang: str) -> Path:
    """
    Translates an SRT file line by line using NLLB-200.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    src_nllb = get_nllb_code(source_lang)
    tgt_nllb = get_nllb_code(target_lang)

    console.print(f"[info]Loading translation model (NLLB-200-600M) on {device.upper()}...[/info]")
    model_name = "facebook/nllb-200-distilled-600M"
    
    # Load the tokenizer and model directly
    tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang=src_nllb)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

    # Load the parsed subtitles
    subs = pysrt.open(str(srt_path))
    console.print(f"[info]Translating {len(subs)} subtitle lines from {src_nllb} to {tgt_nllb}...[/info]")

    # Get the ID for the target language (robust method)
    try:
        forced_bos_token_id = tokenizer.lang_code_to_id[tgt_nllb]
    except AttributeError:
        forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_nllb)

    # Translate line by line with a progress bar
    for sub in track(subs, description="Translating subtitles..."):
        original_text = sub.text.replace('\n', ' ')
        
        if not original_text.strip():
            continue
            
        # Tokenize and move to correct device (CPU/GPU)
        inputs = tokenizer(original_text, return_tensors="pt").to(device)
        
        # Generate translation
        translated_tokens = model.generate(
            **inputs, 
            forced_bos_token_id=forced_bos_token_id, 
            max_length=100
        )
        
        # Decode the output back to text
        translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        
        # Overwrite the subtitle text
        sub.text = translated_text

    # Save the new translated file
    output_path = srt_path.with_name(f"{srt_path.stem}_{target_lang}.srt")
    subs.save(str(output_path), encoding='utf-8')
    
    console.print(f"[success]Translation completed! Saved as: {output_path.name}[/success]")
    return output_path
