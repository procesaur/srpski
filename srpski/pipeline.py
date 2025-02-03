from srpski.helper import *
from srpski.spacyworks import *
import re
import random


def tokenize(text):
    return sentencize(text)


def shuffle_text(text, separator="\n", header=False):

    if not isinstance(text, str):
        text = "\n\n".join(text)

    if header:
        lines = text.split("\n")
        head = lines[0]
        del lines[0]

    text = re.sub(r"\n["+separator+"]+", "\n\n", text)

    sents = text.split("\n\n")
    random.shuffle(sents)
    text = separator.join(sents)

    if header:
        text = head + "\n" + text

    return text


# can work with both string and array
def transliterate(text, typec="lat", dictplus={}, dic={}, aurora=False):

    list = True
    if isinstance(text, str):
        list = False
        text = [text]

    if typec == 'lat':
        if aurora:
            dictplus.update({
                'Dy': 'Dž',
                'Lx': 'Lj',
                'Nx': 'Nj',
                'DY': 'DŽ',
                'LX': 'LJ',
                'NX': 'NJ',
                'lx': 'lj',
                'nx': 'nj',
                'dy': 'dž',
                'Cy': 'Č',
                'Cx': 'Ć',
                'Zx': 'Ž',
                'Dx': 'Đ',
                'Sx': 'Š',
                'cy': 'č',
                'cx': 'ć',
                'zx': 'ž',
                'dx': 'đ',
                'sx': 'š'
            })
        dic.update({
            'Љ': 'Lj',
            'Њ': 'Nj',
            'Џ': 'Dž',
            'А': 'A',
            'Б': 'B',
            'В': 'V',
            'Г': 'G',
            'Д': 'D',
            'Ђ': 'Đ',
            'Е': 'E',
            'Ж': 'Ž',
            'З': 'Z',
            'И': 'I',
            'Ј': 'J',
            'К': 'K',
            'Л': 'L',
            'М': 'M',
            'Н': 'N',
            'О': 'O',
            'П': 'P',
            'Р': 'R',
            'С': 'S',
            'Т': 'T',
            'Ћ': 'Ć',
            'У': 'U',
            'Ф': 'F',
            'Х': 'H',
            'Ц': 'C',
            'Ч': 'Č',
            'Ш': 'Š',
            'љ': 'lj',
            'њ': 'nj',
            'џ': 'dž',
            'а': 'a',
            'б': 'b',
            'в': 'v',
            'г': 'g',
            'д': 'd',
            'ђ': 'đ',
            'е': 'e',
            'ж': 'ž',
            'з': 'z',
            'и': 'i',
            'ј': 'j',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'р': 'r',
            'с': 's',
            'т': 't',
            'ћ': 'ć',
            'у': 'u',
            'ф': 'f',
            'х': 'h',
            'ц': 'c',
            'ч': 'č',
            'ш': 'š'
            })

    if typec == 'cyr':
        if aurora:
            dictplus.update({
                'LX': 'Љ',
                'NX': 'Њ',
                'DY': 'Џ',
                'Lx': 'Љ',
                'Nx': 'Њ',
                'Dy': 'Џ',
                'Dx': 'Ђ',
                'Zx': 'Ж',
                'Cx': 'Ћ',
                'Cy': 'Ч',
                'Sx': 'Ш',
                'lx': 'љ',
                'nx': 'њ',
                'dy': 'џ',
                'dx': 'ђ',
                'zx': 'ж',
                'cx': 'ћ',
                'cy': 'ч',
                'sx': 'ш',
                })
        dic.update({
            'LJ': 'Љ',
            'NJ': 'Њ',
            'DŽ': 'Џ',
            'Lj': 'Љ',
            'Nj': 'Њ',
            'Dž': 'Џ',
            'A': 'А',
            'B': 'Б',
            'V': 'В',
            'G': 'Г',
            'D': 'Д',
            'Đ': 'Ђ',
            'E': 'Е',
            'Ž': 'Ж',
            'Z': 'З',
            'I': 'И',
            'J': 'Ј',
            'K': 'К',
            'L': 'Л',
            'M': 'М',
            'N': 'Н',
            'O': 'О',
            'P': 'П',
            'R': 'Р',
            'S': 'С',
            'T': 'Т',
            'Ć': 'Ћ',
            'U': 'У',
            'F': 'Ф',
            'H': 'Х',
            'C': 'Ц',
            'Č': 'Ч',
            'Š': 'Ш',
            'lj': 'љ',
            'nj': 'њ',
            'dž': 'џ',
            'a': 'а',
            'b': 'б',
            'v': 'в',
            'g': 'г',
            'd': 'д',
            'đ': 'ђ',
            'e': 'е',
            'ž': 'ж',
            'z': 'з',
            'i': 'и',
            'j': 'ј',
            'k': 'к',
            'l': 'л',
            'm': 'м',
            'n': 'н',
            'o': 'о',
            'p': 'п',
            'r': 'р',
            's': 'с',
            't': 'т',
            'ć': 'ћ',
            'u': 'у',
            'f': 'ф',
            'h': 'х',
            'c': 'ц',
            'č': 'ч',
            'š': 'ш'
        })

    dictplus.update(dic)
    mapping = dictplus

    newtext = []
    for x in text:
        for key in mapping.keys():
            x = (x.replace(key, mapping[key]))
        newtext.append(x)
    if list:
        return newtext
    else:
        return newtext[0]


# needs string
def segmentize(text, erase_newlines=True, n=1):

    if erase_newlines:
        control = 12
    else:
        control = 11

    mpa = dict.fromkeys(range(0, control), " ")
    mpa.update(dict.fromkeys(range(12, 32), " "))
    text = text.translate(mpa)
    text = text.replace('<', '\n<').replace('>', '>\n')
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = text.replace('\n \n', '\n').replace(' \n ', '\n')
    text = re.sub(r'\n+', '\n', text)

    segs = text.split('\n')

    if n > 1:
        return chunkses(segs, round(len(segs) / n))

    else:
        return segs


# needs array
def strip_xml(lines, exclusions=False):

    list = True
    if isinstance(lines, str):
        list = False
        lines = lines.replace(">", ">\n").replace("<", "\n<")
        lines = lines.split("\n")
        lines = lines

    exclusion = {}
    noslines = [line.rstrip('\n') for line in lines if line not in ['\n', '']]

    for idx, line in enumerate(noslines):
        if re.match(r"^.*<!--.*$|^.*-->.*$|^.*<.*>.*$", line):
            exclusion[idx] = line
    del noslines

    newlines = [line.rstrip('\n') for line in lines if not re.match(r"^.*<!--.*$|^.*-->.*$|^.*<.*>.*$", line)]

    if not list:
        newlines = "\n".join(newlines)


    if exclusions:
        return newlines, exclusion
    else:
        return newlines


# needs array
def lexmagic(lines, lexicon, synonyms=None, count=False):

    rc = 0
    listexcept = ["„", "“", "”", "*"]
    linesx = ([])

    entries_u, entries_c, entries_l = lexical_entries(lexicon)

    def l(ls):
        for x in ls:
            yield x

    # for each line take word pos and lemma
    for line in l(lines):
        lsplit = line.split('\t')
        if len(lsplit) > 2:
            opos = "\t" + lsplit[1]
            olema = "\t" + lsplit[2]
        elif len(lsplit) == 2:
            opos = "\t" + lsplit[1]
            olema = ""
        else:
            opos = ""
            olema = ""
        word = lsplit[0].rstrip('\n')

        if word != '':

            # if the first letter in a word is capitalized
            if word[0].isupper():
                wordlow = word.lower()  # generate lowercaps word
                wordcap = wordlow.capitalize()  # generate word with a capital

                if word.isupper():
                    if word in entries_u:
                        pass
                    elif wordcap in entries_c:
                        word = wordcap
                        rc += 1

                    elif wordlow in entries_l:
                        word = wordlow
                        rc += 1

                else:
                    if wordcap in entries_c:
                        word = wordcap
                        rc += 1

                    elif wordlow in entries_l:
                        word = wordlow
                        rc += 1

            if word in listexcept:
                word = "\""
                rc += 1

            if synonyms is not None:
                if word in synonyms.keys():
                    word = synonyms[word]
                    rc += 1

        linesx.append(word + opos + olema)

    if count:
        return linesx, rc
    else:
        return linesx


# needs array
def lemmatize(lines, lemdic={}, lexicon="", tagcol=1):

    if lemdic == {}:
        lemdic = lemmas(lexicon)
    newlines = []
    for i, line in enumerate(lines):
        line = line.rstrip()
        pos = line.split('\t')[tagcol]
        word = line.split('\t')[0]
        try:
            newlines.append(line+"\t"+lemdic[word][pos])
        except:
            newlines.append(line+"\t"+word)
    return newlines


# pipe example : tokenize > transliterate > lexmagic > lemmatize
def tag(src, model, lexicon="", pipe=None, probability=False):

    if pipe is None:
        pipe = []

    if isinstance(src, str):
        text = load(src)
    else:
        text = src

    for q in pipe:
        if q != lemmatize:
            if q == magija:
                text = q(text, lexicon)
            else:
                text = q(text)

    text = tag_spacytagger(model, text, probability)

    if lemmatize in pipe:
        text = lemmatize(text, lexicon=lexicon)

    return text


preslovi = transliterate
tokenizuj = tokenize
ucitaj = load
podeli = segmentize
ukloni_xml = strip_xml
reci_iz_recnika = lexical_entries
leme = lemmas
magija = lexmagic
lematizuj = lemmatize
tagiraj = tag
ucitaj_model = load_model
promesaj = shuffle_text
