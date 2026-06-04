import re
import unicodedata


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # Preservar la ñ antes de eliminar diacríticos
    text = text.replace("ñ", "ÑPRESERVE")

    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[̀-ͯ]", "", text)

    text = text.replace("ÑPRESERVE", "ñ")

    text = remove_emojis(text)
    text = re.sub(r"[^\w\s.,\-$%]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002600-\U000026FF"
        "\U00002700-\U000027BF"
        "\U0000FE00-\U0000FE0F"
        "\U0001F900-\U0001F9FF"
        "\U0000200D"
        "\U000020E3"
        "\U0000200B-\U0000200F"
        "\U0000202A-\U0000202E"
        "\U000E0020-\U000E007F"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)
