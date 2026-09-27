"""Source units, court gazetteer and court lexicon.

A *unit* is one author's account inside one EEBO-TCP file. Several TCP files
contain more than one unit (Purchas prints Hawkins, Finch, Roe, Coryat and Saris;
the 1669 Olearius prints Mandelslo; the 1663 Caron prints Schouten), and one
author (Tavernier) is split by the court his books describe.

Fields
------
include / exclude : regular expressions tested against the chain of TEI <head>s
block_from/to     : block-number limits, used where two works share one TEI file without
                    distinguishing headings (Mandelslo's travels follow Olearius's at block 2099)
default_court     : court assigned to a passage unless the gazetteer shows that
                    the passage is about a different court. None = gazetteer only.
"""

UNITS = [
    # ---------------- Mughal ----------------
    dict(unit="roe", tcp="A68617", author="Thomas Roe", observer="English", orig_lang="English",
         translator="", vehicle="Purchas, Pilgrimes (1625), abridged", pub=1625, visit="1615-1619",
         role="Crown ambassador (EIC-funded)", include=r"Iournall of Sir THOMAS ROE", exclude=None,
         default_court="Mughal"),
    dict(unit="hawkins", tcp="A68617", author="William Hawkins", observer="English", orig_lang="English",
         translator="", vehicle="Purchas, Pilgrimes (1625), abridged", pub=1625, visit="1608-1611",
         role="EIC envoy / merchant", include=r"WILLIAM HAVVKINS", exclude=None, default_court="Mughal"),
    dict(unit="finch", tcp="A68617", author="William Finch", observer="English", orig_lang="English",
         translator="", vehicle="Purchas, Pilgrimes (1625), abridged", pub=1625, visit="1608-1611",
         role="EIC merchant", include=r"WILLIAM FINCH", exclude=r"Sierra Leona|SOCOTORA", default_court=None),
    dict(unit="coryat", tcp="A68617", author="Thomas Coryat", observer="English", orig_lang="English",
         translator="", vehicle="Purchas, Pilgrimes (1625)", pub=1625, visit="1615-1617",
         role="private traveller", include=r"THOMAS CORYAT", exclude=None, default_court="Mughal"),
    dict(unit="terry", tcp="A95658", author="Edward Terry", observer="English", orig_lang="English",
         translator="", vehicle="A Voyage to East-India (1655)", pub=1655, visit="1616-1619",
         role="chaplain to Roe's embassy", include=None, exclude=r"COROLLARIE", default_court="Mughal"),
    dict(unit="bernier", tcp="A27515", author="François Bernier", observer="French", orig_lang="French",
         translator="Henry Oldenburg", vehicle="History of the Late Revolution (1676 ed.)", pub=1676,
         visit="1656-1668", role="physician resident at court", include=None, exclude=None,
         default_court="Mughal"),
    dict(unit="tavernier_india", tcp="A63439", author="Jean-Baptiste Tavernier", observer="French",
         orig_lang="French", translator="John Phillips", vehicle="Six Voyages (1677)", pub=1677,
         visit="1640-1667", role="jewel merchant", include=r"TRAVELS IN INDIA", exclude=None,
         default_court=None),
    dict(unit="mandelslo", tcp="A53322", author="Johann Albrecht von Mandelslo", observer="German",
         orig_lang="German", translator="John Davies", vehicle="Olearius, Voyages and Travells (1669)",
         pub=1669, visit="1638-1639", role="gentleman attached to the Holstein embassy",
         include=None, exclude=r"IAPAN|FERMOSA|CHINA", default_court=None, block_from=2099),
    # ---------------- Safavid ----------------
    dict(unit="herbert", tcp="A03065", author="Thomas Herbert", observer="English", orig_lang="English",
         translator="", vehicle="A Relation of Some Yeares Travaile (1634)", pub=1634, visit="1627-1629",
         role="member of Cotton's embassy", include=None, exclude=r"ALPHABETICAL TABLE|ERRATA|Madoc",
         default_court=None),
    dict(unit="olearius", tcp="A53322", author="Adam Olearius", observer="German", orig_lang="German",
         translator="John Davies", vehicle="Voyages and Travells (1669)", pub=1669, visit="1633-1639",
         role="secretary of the Holstein embassy", include=None, exclude=None,
         default_court=None, block_to=2098),
    dict(unit="tavernier_persia", tcp="A63439", author="Jean-Baptiste Tavernier", observer="French",
         orig_lang="French", translator="John Phillips", vehicle="Six Voyages (1677)", pub=1677,
         visit="1632-1668", role="jewel merchant", include=r"PERSIAN TRAVELS|FOURTH BOOK OF THE TRAVELS",
         exclude=None, default_court=None),
    dict(unit="chardin", tcp="A31753", author="Jean Chardin", observer="French", orig_lang="French",
         translator="not named in TCP record", vehicle="Travels into Persia (1686)", pub=1686, visit="1666-1677",
         role="jewel merchant", include=None, exclude=None, default_court=None),
    # ---------------- Qing ----------------
    dict(unit="nieuhof", tcp="A52346", author="Johan Nieuhof", observer="Dutch", orig_lang="Dutch",
         translator="John Ogilby", vehicle="An Embassy ... to the Grand Tartar Cham (1673 ed.)", pub=1673,
         visit="1655-1657", role="steward of the VOC embassy", include=None,
         exclude=r"KIRCHER|Maatzuyker|MAATZUYKER", default_court="Qing"),
    dict(unit="montanus", tcp="A36730", author="Arnoldus Montanus / Olfert Dapper", observer="Dutch",
         orig_lang="Dutch", translator="John Ogilby", vehicle="Atlas Chinensis (1671)", pub=1671,
         visit="1662-1668", role="compiler of VOC embassy journals", include=None,
         exclude=r"Formosa|TAYOWAN", default_court="Qing"),
    dict(unit="brand", tcp="A29216", author="Adam Brand", observer="German (Russian embassy)",
         orig_lang="German", translator="not named in TCP record", vehicle="A Journal of the Embassy (1698)", pub=1698,
         visit="1692-1695", role="secretary of Ides's Russian embassy", include=None,
         exclude=r"Curious OBSERVATIONS", default_court=None),
    dict(unit="lecomte", tcp="A49911", author="Louis Le Comte", observer="French", orig_lang="French",
         translator="not named in TCP record", vehicle="Memoirs and Observations (1697)", pub=1697, visit="1687-1692",
         role="Jesuit mathematician sent by Louis XIV", include=None, exclude=None, default_court="Qing"),
    # ---------------- Siam, Japan, Kandy, others ----------------
    dict(unit="chaumont", tcp="A32752", author="Alexandre de Chaumont", observer="French", orig_lang="French",
         translator="not named in TCP record", vehicle="A Relation of the Late Embassy (1687)", pub=1687,
         visit="1685", role="Louis XIV's ambassador", include=None,
         exclude=r"Journal of the Way|Departure from Bantam", default_court="Siam"),
    dict(unit="schouten", tcp="A34454", author="Joost Schouten", observer="Dutch", orig_lang="Dutch",
         translator="Roger Manley", vehicle="Caron & Schouten, True Description (1663)", pub=1663,
         visit="1624-1636", role="VOC chief at Ayutthaya", include=r"Government, Might, Religion",
         exclude=None, default_court="Siam"),
    dict(unit="caron", tcp="A34454", author="François Caron", observer="Dutch (VOC; Huguenot-born)",
         orig_lang="Dutch", translator="Roger Manley", vehicle="Caron & Schouten, True Description (1663)",
         pub=1663, visit="1619-1641", role="VOC chief at Hirado; audiences at Edo",
         include=r"IAPAN", exclude=r"Government, Might, Religion|Governour of Indiaes|Profits and Advantages",
         default_court="Tokugawa"),
    dict(unit="saris", tcp="A68617", author="John Saris", observer="English", orig_lang="English",
         translator="", vehicle="Purchas, Pilgrimes (1625), abridged", pub=1625, visit="1613",
         role="EIC commander; audience with Ieyasu and Hidetada",
         include=r"Iourney to the Court of the Iaponia|returne to Firando|arriuall at Firando",
         exclude=None, default_court="Tokugawa"),
    dict(unit="knox", tcp="A47586", author="Robert Knox", observer="English", orig_lang="English",
         translator="", vehicle="An Historical Relation of Ceylon (1681)", pub=1681, visit="1660-1679",
         role="captive in the Kandyan kingdom", include=None,
         exclude=r"Malabar Territories|Arrival at Columbo|other Nations|the French", default_court="Kandy"),
    dict(unit="dellavalle", tcp="A65012", author="Pietro della Valle", observer="Italian", orig_lang="Italian",
         translator="George Havers", vehicle="Travels ... into East-India (1665)", pub=1665, visit="1623-1624",
         role="noble traveller; joined a Portuguese embassy to Ikkeri", include=r"Della Valle",
         exclude=None, default_court=None),
    dict(unit="pinto", tcp="A50610", author="Fernão Mendes Pinto", observer="Portuguese", orig_lang="Portuguese",
         translator="Henry Cogan", vehicle="Voyages and Adventures (1653)", pub=1653, visit="1537-1558",
         role="adventurer / trader (account of disputed reliability)", include=None, exclude=None,
         default_court=None),
    dict(unit="tavernier_seraglio", tcp="A63439", author="Jean-Baptiste Tavernier", observer="French",
         orig_lang="French", translator="John Phillips", vehicle="Six Voyages (1677)", pub=1677,
         visit="1630s-1660s", role="jewel merchant (second-hand for the inner seraglio)",
         include=r"SERAGLIO|Seraglio|Gold and Silver-Coins", exclude=r"PERSIAN|INDIA|Persian",
         default_court="Ottoman"),
]

# Gazetteer: ruler titles, capitals and court place-names, in period spellings.
# Matching is case-insensitive on raw text (before normalisation).
GAZETTEER = {
    "Mughal": r"\bmog[ou]ll?s?\b|\bmogor\b|indostan|hindostan|\bagra\b|\bdel+i\b|dehl[iy]|jehan-?abad|gehan-?abad|"
              r"\blahor[e]?\b|aureng|gehangi|iehangi|jehangi|jahangir|shah-?jehan|cha-?jehan|\bakbar|ekbar|"
              r"adsmere|asmere|agimere|brampore|burhanpur|mandoa|\bomrah|amadabad|ahmedabad",
    "Safavid": r"\bpersia|\bispahan|spahawn|spahan|\bsha[h]?[- ]abbas|\bsha[h]?[- ]sefi|\bsha[h]?[- ]soliman|"
               r"\bsophy|\bsophi\b|cazbeen|casbin|kasbin|tauris|ferrabad|farrabaut|\bsolyman|\bkizilbash|"
               r"\bnazar\b|athemat|etmadoulet",
    "Qing": r"\bchina\b|\bchinese|chineses|\bpekin|\bpeking|\bnanking|\bnanquin|cang-?hi|kang-?hi|xun-?chi|"
            r"xunchi|\blipou|colaos|tartar cham|emperor of china|emperour of china",
    "Siam": r"\bsiam|\bsiamese|\bsiammer|\bjudia|\biudia|\bodia\b|\blouvo|barcalon|prauklang|\bpra[- ]?klang",
    "Tokugawa": r"\bjapan|\biapan|iaponi|japoni|\bjedo\b|\biedo\b|\byedo\b|\bedoo\b|\bdayro|\bdairo|"
                r"\bxogun|\bshogun|\bquabo|\bcubo\b|firando|meaco|miaco|ogosho|\bconsamma",
    "Kandy": r"\bcandy\b|\bcande\b|zeilon|ceylon|zeylan|chingula|raja-?singa|\bcolumbo\b",
    "Ottoman": r"grand seignou?r|grand signiou?r|constantinople|\bjanizar|\bjanisar|\bbassa[ws]?\b|ottoman|othoman|\bstambol",
    "Pegu": r"\bpegu|\bbrama[s]?\b|\bava\b|martaban|\btangu\b|\bbramaa",
    "South India": r"venk|ikkeri|ikeri|\bsagher|calicut|samori|zamorin|canara|narsinga|\bolala|banghel",
    "Deccan": r"golcond|golkond|visapou?r|bijapou?r|bisnagar|cutb-?sha|kotb-?sha|\bdecan\b|\bdeccan",
    "Muscovy": r"muscov|moscow|\bczar|\bczaar|\btzar|great duke",
    "Caucasus": r"mingreli|georgia|gurgistan|\bdadian|imiretti|teflis|tiflis",
}

# Words that mark a passage as being *about* rulers and courts. Tested on the
# normalised, lower-cased text. Core terms are required; secondary terms add weight.
COURT_CORE = r"\bkings?\b|\bemperors?\b|\bempress\b|\bqueens?\b|\bshah\b|\bsultan\b|\bmogul\b|\bmogol\b|" \
             r"\bmajesty\b|\bcourt\b|\bthrone\b|\baudience\b|\bpalace\b|\bambassadors?\b|\bembassy\b|\bembassage\b"
COURT_SECONDARY = r"\bprinces?\b|\bnobles?\b|\bnobility\b|\blords?\b|\bomrahs?\b|\bgrandees?\b|\beunuchs?\b|" \
                  r"\bceremon\w*|\bprostrat\w*|\bbow\w*\b|\bknee\w*\b|\bpresents?\b|\bgifts?\b|\bfavou?rites?\b|" \
                  r"\bcouncil\w*\b|\bministers?\b|\bofficers?\b|\bguards?\b|\battend\w*\b|\btribute\b|\bcrown\w*\b|" \
                  r"\breign\w*\b|\btyran\w*\b|\bjustice\b|\brevenues?\b|\bseraglio\b|\bharem\b|\bconcubines?\b|" \
                  r"\bwives\b|\bfeast\w*\b|\bbanquet\w*\b|\belephants?\b|\bhorses?\b|\bjewels?\b|\bgold\b|" \
                  r"\btitles?\b|\bslaves?\b|\bvassals?\b|\bsubjects?\b|\bcommand\w*\b|\bpunish\w*\b|\bexecut\w*\b"
