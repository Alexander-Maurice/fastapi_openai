
def clean_surrogates(text):
    if isinstance(text, str):
        return text.encode('utf-8', errors='ignore').decode('utf-8')
    return text


