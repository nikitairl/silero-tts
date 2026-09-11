import re

# ── Кардинальные числительные ──────────────────────────────────
ONES = ["", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
TEENS = [
    "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать",
    "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать",
]
TENS = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят",
        "семьдесят", "восемьдесят", "девяносто"]
HUNDREDS = ["", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот",
            "семьсот", "восемьсот", "девятьсот"]

SCALES = [
    (10 ** 9, ("миллиард", "миллиарда", "миллиардов")),
    (10 ** 6, ("миллион", "миллиона", "миллионов")),
    (10 ** 3, ("тысяча", "тысячи", "тысяч")),
]

# ── Порядковые числительные ────────────────────────────────────
ONES_ORD = ["", "первый", "второй", "третий", "четвёртый", "пятый", "шестой",
            "седьмой", "восьмой", "девятый"]
TEENS_ORD = ["десятый", "одиннадцатый", "двенадцатый", "тринадцатый",
             "четырнадцатый", "пятнадцатый", "шестнадцатый", "семнадцатый",
             "восемнадцатый", "девятнадцатый"]
TENS_ORD = ["", "", "двадцатый", "тридцатый", "сороковой", "пятидесятый",
            "шестидесятый", "семидесятый", "восьмидесятый", "девяностый"]
HUNDREDS_ORD = ["", "сотый", "двухсотый", "трёхсотый", "четырёхсотый",
                "пятисотый", "шестисотый", "семисотый", "восьмисотый", "девятисотый"]

_THOUSAND_ORD = {
    1: "тысячный", 2: "двухтысячный", 3: "трёхтысячный", 4: "четырёхтысячный",
    5: "пятитысячный", 6: "шеститысячный", 7: "семитысячный", 8: "восьмитысячный",
    9: "девятитысячный",
}

DAYS_ORD = ["", "первое", "второе", "третье", "четвёртое", "пятое", "шестое",
            "седьмое", "восьмое", "девятое", "десятое", "одиннадцатое",
            "двенадцатое", "тринадцатое", "четырнадцатое", "пятнадцатое",
            "шестнадцатое", "семнадцатое", "восемнадцатое", "девятнадцатое",
            "двадцатое", "двадцать первое", "двадцать второе", "двадцать третье",
            "двадцать четвёртое", "двадцать пятое", "двадцать шестое",
            "двадцать седьмое", "двадцать восьмое", "двадцать девятое",
            "тридцатое", "тридцать первое"]

MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
              "августа", "сентября", "октября", "ноября", "декабря"]


def _plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    n = n % 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


def _under_1000(n, feminine=False):
    words = []
    h = n // 100
    if h:
        words.append(HUNDREDS[h])
    rem = n % 100
    if rem:
        t = rem // 10
        o = rem % 10
        if t == 1:
            words.append(TEENS[o])
        else:
            if t:
                words.append(TENS[t])
            if o:
                if o == 1:
                    words.append("одна" if feminine else "один")
                elif o == 2:
                    words.append("две" if feminine else "два")
                else:
                    words.append(ONES[o])
    return " ".join(words)


def number_to_words(value):
    value = int(value)
    if value == 0:
        return "ноль"
    parts = []
    for scale, forms in SCALES:
        if value >= scale:
            chunk = value // scale
            value %= scale
            feminine = scale == 10 ** 3
            parts.append(_under_1000(chunk, feminine) + " " + _plural(chunk, *forms))
    if value:
        parts.append(_under_1000(value, False))
    return " ".join(parts)


def _ordinal_nom(n):
    if n % 100 == 0:
        return HUNDREDS_ORD[n // 100]
    words = []
    h = n // 100
    if h:
        words.append(HUNDREDS[h])
    rem = n % 100
    if rem % 10 == 0:
        words.append(TENS_ORD[rem // 10])
    else:
        t = rem // 10
        o = rem % 10
        if t == 1:
            words.append(TEENS_ORD[o])
        else:
            if t:
                words.append(TENS[t])
            if o:
                words.append(ONES_ORD[o])
    return " ".join(words)


def _decline(ord_word, case):
    if case == "nom" or ord_word == "":
        return ord_word
    endings = {
        "gen": {"ий": "его", "ый": "ого", "ой": "ого"},
        "prep": {"ий": "ем", "ый": "ом", "ой": "ом"},
        "dat": {"ий": "ему", "ый": "ому", "ой": "ому"},
    }
    for suffix, repl in endings[case].items():
        if ord_word.endswith(suffix):
            return ord_word[: -len(suffix)] + repl
    return ord_word


def year_to_words(year, case="nom"):
    year = int(year)
    if year == 0:
        return _decline("нулевой", case)
    if year % 1000 == 0 and year // 1000 in _THOUSAND_ORD:
        return _decline(_THOUSAND_ORD[year // 1000], case)
    parts = []
    k = year // 1000
    rest = year % 1000
    if k:
        if k == 1:
            parts.append("тысяча")
        else:
            parts.append(_under_1000(k, feminine=True) + " " + _plural(k, "тысяча", "тысячи", "тысяч"))
    if rest:
        parts.append(_decline(_ordinal_nom(rest), case))
    return " ".join(parts)


# ── Даты ───────────────────────────────────────────────────────
_DATE_RE = re.compile(r"(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?")


def _process_date(m):
    day = int(m.group(1))
    month = int(m.group(2))
    year = m.group(3)
    if not (1 <= day <= 31 and 1 <= month <= 12):
        return m.group(0)
    out = DAYS_ORD[day] + " " + MONTHS_GEN[month - 1]
    if year is not None:
        out += " " + year_to_words(year, "gen") + " года"
    return out


# ── Годы (порядковые) ──────────────────────────────────────────
_YEAR_CASE = {
    "год": "nom", "года": "gen", "году": "prep", "годе": "prep",
    "годов": "gen", "годам": "dat", "годами": "nom", "годах": "prep",
    "г": "nom", "гг": "gen", "гг.": "gen", "г.": "nom",
}
_YEAR_RE = re.compile(r"(\d{3,4})\s+(год(?:а|у|е|ов|ам|ами|ах)?|гг?\.?)")
_IN_YEAR_RE = re.compile(r"(?<=[вВ]\s)(\d{4})(?=\s|$|[^\d])")


def _process_year(m):
    num = int(m.group(1))
    word = m.group(2)
    case = _YEAR_CASE.get(word.rstrip("."), "nom")
    return year_to_words(num, case) + " " + word


# ── Обычные числа и дроби ──────────────────────────────────────
_NUMBER_RE = re.compile(r"\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?")


def _fraction(num_str):
    n = int(num_str)
    if n == 0:
        return "ноль"
    length = len(num_str)
    if length == 1:
        denom = ("десятая", "десятых")
    elif length == 2:
        denom = ("сотая", "сотых")
    elif length == 3:
        denom = ("тысячная", "тысячных")
    else:
        return " ".join(number_to_words(int(d)) for d in num_str)
    num_word = _under_1000(n, feminine=True)
    denom_word = _plural(n, denom[0], denom[1], denom[1])
    return num_word + " " + denom_word


def _convert_token(tok):
    s = tok.replace(" ", "").replace("\u00a0", "")
    for sep in (",", "."):
        if sep in s:
            int_part, frac_part = s.split(sep, 1)
            whole = number_to_words(int(int_part))
            return f"{whole} целых {_fraction(frac_part)}"
    return number_to_words(s)


def _plain_numbers(text):
    out = []
    last = 0
    for m in _NUMBER_RE.finditer(text):
        word = _convert_token(m.group(0))
        if m.start() > 0 and text[m.start() - 1].isalpha():
            word = " " + word
        out.append(text[last:m.start()])
        out.append(word)
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def numbers_to_text(text):
    text = _DATE_RE.sub(_process_date, text)
    text = _YEAR_RE.sub(_process_year, text)
    text = _IN_YEAR_RE.sub(lambda m: year_to_words(int(m.group(1)), "prep"), text)
    return _plain_numbers(text)
