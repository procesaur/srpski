import random
import re
import os
import sys
import requests
import zipfile
import io
from pathlib import Path


def load_model(file):
    if 'https' in file or 'http' in file:
        response = requests.get(file)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall()

    elif os.path.isfile(file):
        with zipfile.ZipFile(file, 'r') as z:
            z.extractall()

    return Path(file).stem

def load(file, size=False):
    if 'https' in file or 'http' in file:
        response = requests.get(file)
        response.encoding = response.apparent_encoding
        x = sys.argv
        fulltext = response.text.replace('\r', '')



        response = requests.head(file, allow_redirects=True)
        sizeX = response.headers.get('content-length', -1)

    elif os.path.isfile(file):
        sizeX = os.path.getsize(file)
        try:
            with open(file, 'r', encoding='utf-8') as f:
                fulltext = f.read()

        except:
            with open(file, 'r', encoding='latin2') as f:
                fulltext = f.read()
    else:
        fulltext = file
        sizeX = 1

    if size:
        return fulltext, sizeX
    else:
        return fulltext


def chunkses(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def ratio_split(ratio, lst):
    count_sen = 0
    # remove new lines form the end of each line, because they are an array now
    for i, line in enumerate(lst):
        lst[i] = line.rstrip('\n')
        # check if line is empty, increase, sentence counter
        if lst[i] == "":
            count_sen += 1

    # check if text is split to sentences (is there count_sen), if not try to split by SENT tag.
    if count_sen < 1:
        # now add newline after each SENT, we are trying to break text into sentences
        for i, line in enumerate(lst):
            if 'SENT' in line:
                lst[i] = lst[i] + '\n'
    # create sentence array
    text = re.sub(r'\n\n+', '\n\n', '\n'.join(lst)).strip()
    sentences = text.split('\n\n')
    # we set chunk sizes to X% of text - this will be used for training
    chunksize = len(sentences) * ratio

    # strip any extra newlines
    for i, sent in enumerate(sentences):
        if sent.endswith('\n'):
            sentences[i] = sent.rstrip('\n')

    # randomly shuffle sentences to get unbiased corpora
    random.shuffle(sentences)
    # initialize are chunks
    train = ([])
    tune = ([])
    # add first 90% of sentences to "ninety" array, and the rest to "ten" array
    for i, sent in enumerate(sentences):
        if i < chunksize:
            train.append(sent + "\n\n")
        else:
            tune.append(sent + "\n\n")

    return train, tune


def training_prep(file):
    lines = load(file)
    tagsets = {}
    meta = lines[0].rstrip().split("\t")
    colsn = len(meta)
    del lines[0]

    newline = ""
    for i in range(1, colsn):
        newline += "\t"
    newline += "\n"

    lemacol = -1
    for i, m in enumerate(meta):
        if i > 0:
            if m != "lemma" and m != "lema":
                tagsets[m] = i
            else:
                lemacol = i

    for i, line in enumerate(lines):
        if line in ['\n', '', '\0', newline]:
            lines[i] = '\n'

    return lines, lemacol, tagsets, newline, colsn


def filechunkses(paragraphs, n, total):
    avg = round(total/n)
    le = 0
    plist = ([])
    for i, p in enumerate(paragraphs):
        plist.append(p)
        le += len(p)
        if le > avg or i+1 == len(paragraphs):
            yield plist
            le = 0
            plist = ([])


def lexical_entries(lex_path):
    lexicon = load(lex_path).split('\n')

    entriesfull = [wordx.split('\t')[0] for wordx in lexicon if wordx not in ['\n', '']]

    entries_c = [wordx for wordx in entriesfull if wordx[0].isupper()]
    entries_l = [wordx for wordx in entriesfull if not wordx[0].isupper()]
    entries_u = [wordx for wordx in entries_c if wordx.isupper()]
    entries_c += [wordx for wordx in entries_c if not wordx.isupper()]

    return entries_u, entries_c, entries_l


def lemmas(lexicons):

    if isinstance(lexicons, str):
        lemmatizers = [lexicons]
    else:
        lemmatizers = lexicons

    lemdic = {}
    for lexicon in lemmatizers:

        diclines = load(lexicon).split("\n")

        for d in diclines:
            tabs = d.split("\t")
            ent = tabs[0]
            lemdic[ent] = {}
            del tabs[0]
            for t in tabs:
                try:
                    lemdic[ent][t.split(" ")[0]] = t.split(" ")[1].rstrip()
                except:
                    pass
    return lemdic
