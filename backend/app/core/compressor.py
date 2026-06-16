from scaledown import ScaleDownCompressor

_compressor = None


def get_compressor():
    global _compressor
    if _compressor is None:
        _compressor = ScaleDownCompressor(
            target_model='gemini-1.5-flash',
            rate='auto',
        )
    return _compressor


def compress_context(context: str, prompt: str) -> tuple[str, int, int]:
    """Returns (compressed_text, original_tokens, compressed_tokens)"""
    result = get_compressor().compress(
        context=context,
        prompt=prompt,
    )
    orig = result.metrics.original_prompt_tokens
    compr = result.metrics.compressed_prompt_tokens
    return result.content, orig, compr
