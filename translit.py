import re

# Частые слова, которые плохо проходят через таблицу, — озвучиваются как есть.
# Ключи — нижний регистр. Расширяй по мере надобности.
OVERRIDES = {
    # бренд станции и радио-слова
    "subwave": "сабвейв",
    "radio": "радио",
    "fm": "эфэм",
    "am": "эйэм",
    "dj": "диджей",
    "feat": "фит",
    "ft": "фит",
    "featuring": "фитуринг",
    "vs": "против",
    "live": "лайв",
    "remix": "ремикс",
    "mix": "микс",
    "edit": "эдит",
    "version": "версия",
    "intro": "интро",
    "outro": "аутро",
    "track": "трек",
    "single": "сингл",
    "album": "альбом",
    "cover": "кавер",
    "acoustic": "акустик",
    "bonus": "бонус",
    "playlist": "плейлист",
    "show": "шоу",
    "hit": "хит",
    "chart": "чарт",
    "top": "топ",
    "new": "нью",
    "best": "бест",
    "style": "стайл",
    "party": "пати",
    "dance": "дэнс",
    # жанры
    "rock": "рок",
    "pop": "поп",
    "rap": "рэп",
    "jazz": "джаз",
    "blues": "блюз",
    "soul": "соул",
    "house": "хаус",
    "techno": "техно",
    "trance": "транс",
    "punk": "панк",
    "metal": "метал",
    "classic": "классик",
    # ходовые английские слова, где транслит дал бы мусор
    "the": "зэ",
    "you": "ю",
    "your": "йор",
    "and": "энд",
    "of": "оф",
    "with": "виз",
    "without": "визаут",
    "night": "найт",
    "tonight": "тунайт",
    "today": "тудей",
    "light": "лайт",
    "lights": "лайтс",
    "fight": "файт",
    "right": "райт",
    "high": "хай",
    "life": "лайф",
    "time": "тайм",
    "fire": "файр",
    "love": "лав",
    "dream": "дрим",
    "world": "ворлд",
    "school": "скул",
    "girl": "гёрл",
    "boy": "бой",
    "man": "мэн",
    "woman": "вумен",
    "forever": "форевер",
    "never": "невер",
    "again": "эгейн",
    "enter": "энтер",
    "sound": "саунд",
    "wave": "вейв",
    "music": "мьюзик",
    "power": "пауэр",
    "game": "гейм",
    "star": "стар",
    "street": "стрит",
    "city": "сити",
    "heart": "харт",
    "blood": "блад",
    "black": "блэк",
    "white": "вайт",
    "blue": "блю",
    "red": "ред",
    "snake": "снейк",
    # имена/бренды, которые сложно вывести таблицей
    "youtube": "ютуб",
    "google": "гугл",
    "spotify": "спотифай",
    "netflix": "нетфликс",
    "apple": "эппл",
    "iphone": "айфон",
    "tiktok": "тикток",
    "instagram": "инстаграм",
    "whatsapp": "ватсап",
    "nirvana": "нирвана",
    "metallica": "металлика",
    "beatles": "битлз",
    "weeknd": "уикнд",
    "weekend": "уикенд",
    "blinding": "блайндинг",
    "queen": "квин",
    "eminem": "эминем",
    "rihanna": "риана",
    "beyonce": "бейонсе",
    "shakira": "шакира",
    "taylor": "тейлор",
    "swift": "свифт",
    "adele": "адель",
    "sheeran": "ширан",
}

# Диграфы идут первыми (длинные → короткие), чтобы "sh" не развалился на "с"+"х".
_DIGRAPHS = [
    ("sch", "ш"),
    ("tch", "ч"),
    ("sh", "ш"),
    ("zh", "ж"),
    ("ch", "ч"),
    ("kh", "х"),
    ("th", "т"),
    ("ph", "ф"),
    ("gh", "г"),
    ("wh", "в"),
    ("qu", "кв"),
    ("ck", "к"),
    ("ng", "нг"),
    ("ee", "и"),
    ("ea", "и"),
    ("oo", "у"),
    ("ou", "ау"),
    ("ow", "ау"),
    ("ay", "эй"),
    ("ey", "эй"),
    ("oy", "ой"),
    ("ai", "эй"),
    ("ei", "эй"),
    ("oa", "о"),
    ("ie", "и"),
    ("au", "ау"),
    ("aw", "о"),
    ("ce", "с"),
    ("ci", "с"),
    ("cy", "с"),
    ("ya", "я"),
    ("yo", "йо"),
    ("yu", "ю"),
    ("ye", "е"),
]

_SINGLE = {
    "a": "а",
    "b": "б",
    "c": "к",
    "d": "д",
    "e": "е",
    "f": "ф",
    "g": "г",
    "h": "х",
    "i": "и",
    "j": "дж",
    "k": "к",
    "l": "л",
    "m": "м",
    "n": "н",
    "o": "о",
    "p": "п",
    "q": "к",
    "r": "р",
    "s": "с",
    "t": "т",
    "u": "у",
    "v": "в",
    "w": "в",
    "x": "кс",
    "y": "й",
    "z": "з",
}

_MAP = {}
for _k, _v in _DIGRAPHS:
    _MAP[_k] = _v
for _k, _v in _SINGLE.items():
    _MAP[_k] = _v

_FALLBACK_RE = re.compile(
    "|".join(re.escape(k) for k in sorted(_MAP, key=len, reverse=True))
)
_WORD_RE = re.compile(r"[A-Za-z]+")


def _fallback(word_lower: str) -> str:
    return _FALLBACK_RE.sub(lambda m: _MAP[m.group(0)], word_lower)


def transliterate_word(word: str) -> str:
    cap = word[:1].isupper()
    key = word.lower()
    out = OVERRIDES.get(key, _fallback(key))
    if cap and out:
        out = out[0].upper() + out[1:]
    return out


def transliterate_latin(text: str) -> str:
    return _WORD_RE.sub(lambda m: transliterate_word(m.group(0)), text)
