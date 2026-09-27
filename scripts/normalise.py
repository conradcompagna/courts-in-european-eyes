"""Light, rule-based spelling normalisation for seventeenth-century English print.

This is deliberately conservative and fully inspectable. It regularises
typographic conventions (u/v, i/j, vv) and a short list of frequent variant
spellings. It does not modernise vocabulary, syntax or proper names.
Students compare embeddings of raw and normalised text in Stage 3.
"""
import re

VOWELS = "aeiouAEIOU"

WORD_MAP = {
    # function words and very frequent variants
    "doe": "do", "goe": "go", "beene": "been", "bin": "been", "onely": "only",
    "owne": "own", "selfe": "self", "himselfe": "himself", "themselues": "themselves",
    "themselfes": "themselves", "shee": "she", "hee": "he", "wee": "we", "mee": "me",
    "sayd": "said", "saide": "said", "dayes": "days", "wayes": "ways", "yeare": "year",
    "yeares": "years", "cittie": "city", "citie": "city", "citty": "city", "cities": "cities",
    "kingdome": "kingdom", "kingdomes": "kingdoms", "countrey": "country", "countreys": "countries",
    "countrie": "country", "souldiers": "soldiers", "souldier": "soldier", "emperour": "emperor",
    "emperours": "emperors", "embassador": "ambassador", "embassadour": "ambassador",
    "ambassadour": "ambassador", "embassadors": "ambassadors", "embassadours": "ambassadors",
    "ambassadours": "ambassadors", "embassadress": "ambassadress", "maiestie": "majesty",
    "maiesty": "majesty", "maiesties": "majesty's", "subiects": "subjects", "subiect": "subject",
    "iewels": "jewels", "iewells": "jewels", "iewell": "jewel", "chaire": "chair",
    "vntill": "until", "till": "till", "vnto": "unto", "vpon": "upon", "vs": "us",
    "neere": "near", "heere": "here", "there": "there", "bee": "be", "shew": "show",
    "shewed": "showed", "shewn": "shown", "shewing": "showing", "ioy": "joy", "iudge": "judge",
    "tooke": "took", "gaue": "gave", "haue": "have", "hauing": "having", "giue": "give",
    "diuers": "divers", "euery": "every", "euer": "ever", "neuer": "never", "ouer": "over",
    "seuerall": "several", "seueral": "several", "great": "great", "musique": "music",
    "publique": "public", "physick": "physic", "heretofore": "heretofore", "whilest": "whilst",
    "sonne": "son", "sonnes": "sons", "wife": "wife", "yong": "young", "dyed": "died",
    "chuse": "choose", "vertue": "virtue", "cloathes": "clothes", "cloaths": "clothes",
    "roome": "room", "roomes": "rooms", "mony": "money", "monie": "money", "pallace": "palace",
    "pallaces": "palaces", "throan": "throne", "trone": "throne", "audiance": "audience",
}

_word = re.compile(r"[A-Za-z]+")


def _match_case(src: str, tgt: str) -> str:
    if src.isupper() and len(src) > 1:
        return tgt.upper()
    if src[0].isupper():
        return tgt[0].upper() + tgt[1:]
    return tgt


def _norm_word(w: str) -> str:
    lw = w.lower()
    if lw in WORD_MAP:
        return _match_case(w, WORD_MAP[lw])
    x = w
    # vv -> w
    x = x.replace("VV", "W").replace("Vv", "W").replace("vv", "w")
    # initial v before a consonant -> u  (vnto, vpon, vse)
    if len(x) > 1 and x[0] in "vV" and x[1] not in VOWELS:
        x = ("u" if x[0] == "v" else "U") + x[1:]
    # medial u between vowels -> v (haue, giue, seuerall), not after q
    chars = list(x)
    for i in range(1, len(chars) - 1):
        if chars[i] in "uU" and chars[i - 1] in VOWELS and chars[i + 1] in VOWELS and chars[i - 1] not in "qQ":
            # 'qu' already excluded; avoid 'uu'
            chars[i] = "v" if chars[i] == "u" else "V"
    x = "".join(chars)
    # initial i/I before a vowel -> j/J (Iapan, iourney, Iesuits); not 'Ia' in 'Iambic' (rare)
    if len(x) > 2 and x[0] in "iI" and x[1] in "aeouAEOU":
        x = ("j" if x[0] == "i" else "J") + x[1:]
    lx = x.lower()
    # -ie -> -y in longer words (citie, countrie, companie)
    if len(lx) >= 5 and lx.endswith("ie") and lx[-3] not in VOWELS:
        x = x[:-2] + ("Y" if x[-1].isupper() else "y")
    elif len(lx) >= 6 and lx.endswith("ies") is False and lx.endswith("ll") and lx[-3] in "au" and not lx.endswith("shall"):
        # generall -> general, beautifull -> beautiful
        x = x[:-1]
    return x


def normalise(text: str) -> str:
    text = text.replace("&", "and")
    return _word.sub(lambda m: _norm_word(m.group(0)), text)


def change_rate(text: str) -> float:
    """Share of word tokens altered by normalise() -- a rough index of orthographic distance."""
    words = _word.findall(text.replace("&", "and"))
    if not words:
        return 0.0
    changed = sum(1 for w in words if _norm_word(w) != w)
    return changed / len(words)


if __name__ == "__main__":
    s = ("The Ambassadour hauing giuen his presents vnto the Emperour of Iapan, "
         "wee were conducted to the Pallace, where the King sate vpon a Throne of seuerall "
         "iewels & the generall of his souldiers stood neere him in the Citie.")
    print(normalise(s))
