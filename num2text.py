import re

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


# Число: целое (с пробельными тысячными группами) либо десятичное (один разделитель).
_NUMBER_RE = re.compile(r"\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?")


def _convert_token(tok):
    s = tok.replace(" ", "").replace("\u00a0", "")
    for sep in (",", "."):
        if sep in s:
            int_part, frac_part = s.split(sep, 1)
            whole = number_to_words(int(int_part))
            return f"{whole} целых {_fraction(frac_part)}"
    return number_to_words(s)


def numbers_to_text(text):
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
