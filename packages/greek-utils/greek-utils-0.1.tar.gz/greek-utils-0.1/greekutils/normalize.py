from .trigrams import trigrams

from pysblgnt import morphgnt_rows

import unicodedata

VARIA = "\u0300"
OXIA = "\u0301"
PSILI = "\u0313"
DASIA = "\u0314"
PERISPOMENI = "\u0342"

ACCENTS = [VARIA, OXIA, PERISPOMENI]

def d(s):
    return unicodedata.normalize("NFD", s)

def n(x):
    return unicodedata.normalize("NFKC", x)

def count_accents(s):
    count = 0
    for c in d(s):
        if c in ACCENTS:
            count += 1
    return count

def strip_accents(s):
    return ''.join((c for c in d(s) if unicodedata.category(c) != "Mn"))

def strip_last_accent(word):
    x = list(word)
    for i, ch in enumerate(x[::-1]):
        s = strip_accents(ch)
        if s != ch:
            x[-i - 1] = s
            break
    return "".join(x)

ELISION = [
    "ἀλλά",
    "ἀντί",
    "ἀπό",
    "δέ",
    "διά",
    "ἐπί",
    "κατά",
    "μετά",
    "οὐδέ",
    "μηδέ",
    "παρά",
    "τοῦτο",
    "ταῦτα",
    "ὑπό",
]

elision_dict = {}
for word in ELISION:
    elided = d(word[:-1]) + "\u2019"
    elision_dict[elided] = word
    if elided[-2] == "τ":
        elision_dict[elided[:-2] + "θ\u2019"] = word
    elif elided[-2] == "π":
        elision_dict[elided[:-2] + "φ\u2019"] = word

CLITICS = [
    "εἰμί",
    "εἰσίν",
    "ἐσμέν",
    "ἐστέ",
    "γέ",
    "ποτέ",
    "τέ",
    "φησίν",
    "πώς",
    "ποῦ",
    "φημί",
]

clitics_dict = {}
for word in CLITICS:
    clitics_dict[strip_last_accent(word)] = word

if __name__ == "__main__":

    for book_num in [23, 24, 25, 26]:
        for prev_row, row, next_row in trigrams(morphgnt_rows(book_num)):

            if row["word"] in [
                # proper nouns
                "Ἰούδας",
                "Ἰησοῦ",
                "Ἰησοῦν",
                "Ἰησοῦς",
                "Χριστοῦ",
                "Χριστὸν",
                "Χριστῷ",
                "Ἰακώβου",
                "Αἰγύπτου",
                "Σόδομα",
                "Γόμορρα",
                "Μιχαὴλ",
                "Μωϋσέως",
                "Κάϊν",
                "Βαλαὰμ",
                "Κόρε",
                "Ἀδὰμ",
                "Ἑνὼχ",
                "Γαΐῳ",
                "Διοτρέφης",
                "Δημητρίῳ",
                "Χριστός",

                "χριστός",
                "χριστὸς",

                # end in σιν but aren't σι(ν)
                "κρίσιν",
                "κόλασιν",

                # end in ε but aren't ε(ν)
                "σε",
                "ὅτε",
                "οὔτε",
                "πώποτε",

                "μνήσθητε",
                "τηρήσατε",
                "ἐλεᾶτε",
                "σῴζετε",
                "ἠκούσατε",
                "περιπατῆτε",
                "βλέπετε",
                "ἀπολέσητε",
                "ἀπολάβητε",
                "λαμβάνετε",
                "λέγετε",
                "ἔχητε",
                "ἁμάρτητε",
                "εἴχετε",
                "ἐγνώκατε",
                "νενικήκατε",
                "ἀγαπᾶτε",
                "ἔχετε",
                "οἴδατε",
                "μενεῖτε",
                "ἐλάβετε",
                "μένετε",
                "εἰδῆτε",
                "γινώσκετε",
                "ἴδετε",
                "κληθῶμεν",
                "οἴδαμεν",
                "θαυμάζετε",
                "πιστεύετε",
                "δοκιμάζετε",
                "ἀκηκόατε",
                "φυλάξατε",

                # end in εν but aren't ε(ν)
                "ὀφείλομεν",
                "μαρτυροῦμεν",
                "λαλήσομεν",
                "ἐλάβομεν",
                "εἴχομεν",
                "ἀγαπῶμεν",
                "περιπατῶμεν",
                "ἀκηκόαμεν",
                "ἑωράκαμεν",
                "ἀπαγγέλλομεν",
                "γράφομεν",
                "ἀναγγέλλομεν",
                "εἴπωμεν",
                "ἔχομεν",
                "ποιοῦμεν",
                "πλανῶμεν",
                "ὁμολογῶμεν",
                "ἡμαρτήκαμεν",
                "γινώσκομεν",
                "ἐγνώκαμεν",
                "τηρῶμεν",
                "σχῶμεν",
                "αἰσχυνθῶμεν",
                "μεταβεβήκαμεν",
                "πείσομεν",
                "αἰτῶμεν",
                "λαμβάνομεν",
                "τηροῦμεν",
                "πιστεύσωμεν",
                "ζήσωμεν",
                "ἠγαπήκαμεν",
                "μένομεν",
                "πεπιστεύκαμεν",
                "ἔχωμεν",
                "ποιῶμεν",
                "γινώσκωμεν",
                "ᾐτήκαμεν",
                "οἴδαμεν",
                "Οἴδαμεν",

                "ὅθεν",
                "ἔμπροσθεν",
            ]:
                continue

            word = row["word"]
            actual_norm = row["norm"]

            word = word.lower()

            # change graves to acutes

            temp = ""
            for ch in d(word):
                if ch == VARIA:
                    ch = OXIA  # OXIA will be normalized to TONOS below if needed
                temp += ch
            norm = n(temp)

            #

            if count_accents(norm) == 2:
                norm = strip_last_accent(norm)
                assert count_accents(norm) == 1

                # @@@ test following word?

            # normalize movable nu in 3rd person verb

            if norm not in clitics_dict:
                if norm.endswith("εν"):
                    norm = norm[:-1] + "(ν)"
                if norm.endswith("ε"):
                    norm = norm + "(ν)"

            # if no accent on a clitic, add one to normalization

            if count_accents(norm) == 0:
                if norm in clitics_dict:
                    norm = clitics_dict[norm]

            #

            if (
                norm.endswith("σιν") or
                norm.endswith("σίν") or
                norm.endswith("ξίν") or
                norm.endswith("ξιν")
            ):
                norm = norm[:-1] + "(ν)"

            #

            if norm in ["ἐστιν", "ἔστιν", "ἐστίν"]:  # check following?
                norm = "ἐστί(ν)"

            #

            if norm == u"ἐξ":
                norm = u"ἐκ"

            if norm in ["οὐκ", "οὐχ"]:
                norm = "οὐ"

            if norm in [u"μέχρι", u"μέχρις"]:
                norm = u"μέχρι(ς)"

            if norm in [u"οὕτω", u"οὕτως"]:
                norm = u"οὕτω(ς)"

            # elision

            if norm.endswith("\u2019"):
                if d(norm) in elision_dict:
                    norm = elision_dict[d(norm)]

            # proclitics

            if norm == u"εἴ":
                norm = u"εἰ"
            elif norm == u"εἴς":
                norm = u"εἰς"
            elif norm == u"ἔν":
                norm = u"ἐν"
            # elif norm == u"ὅ":  # @@@  check following
            #     norm = u"ὁ"
            elif norm == u"ὥς":
                norm = u"ὡς"

            ###

            if norm != actual_norm:
                print(norm, actual_norm)
                print(prev_row)
                print(row)
                print(next_row)
                quit()
