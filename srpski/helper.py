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

reldir = os.path.dirname(os.path.abspath(__file__))
xml = r'</?[šđžćč\-_\w]+( [šđžćč\-_\w]+=["\'].*["\'])*/?>'


def read_abbrevs(file):
    abbrevs = {'B': [], 'N': [], 'S': []}
    for line in open(os.path.join(reldir, file), encoding='utf8'):
        if not line.startswith('#'):
            abbrev, type = line.strip().split('\t')[:2]
            abbrevs[type].append(abbrev)
    return abbrevs


abbrevs = {
    'sr': read_abbrevs('sr.abbrev'),
}

num = r'(?:(?<!\d)[+-])?\d+(?:[.,:/]\d+)*(?:[.](?!\.)|-[^\W\d_]+)?'
# emoswithspaces emoticon=r'[=:;8][\'-]*(?:\s?\)+|\s?\(+|\s?\]+|\s?\[
# +|\sd\b|\sp\b|d+\b|p+\b|s+\b|o+\b|/|\\|\$|\*+)|-\.-|\^_\^|\([\W]+\)|<3|</3|<\\3|\\o/'
emoticon = r'[=:;8][\'-]*(?:\)+|\(+|\]+|\[+|d\b|p\b|d+\b|p+\b|s+\b|o+\b|/|\\|\$|\*+)|-\.-|\^_\^|\([' \
           r'^\w\s]+\)|<3|</3|<\\3|\\o/ '
word = r'(?:[*]{2,})?\w+(?:[@­\'-]\w+|[*]+\w+)*(?:[*]{2,})?'

langs = {

    'sr': {
        'abbrev': r'|'.join(abbrevs['sr']['B'] + abbrevs['sr']['N'] + abbrevs['sr']['S']),
        'num': num,
        'url': r'https?://[-\w/%]+(?:[.#?=&@;][-\w/%]+)+|\b\w+\.(?:\w+\.)?('
               r'?:com|org|net|gov|edu|int|io|eu|si|hr|rs|ba|me|mk|it|at|hu|bg|ro|al|de|ch|be|dk|se|no|es|pt|ie|fr|fi'
               r'|cl|co|bo|br|gr|ru|uk|us|by|cz|sk|pl|lt|lv|lu|ca|in|tr|il|iq|ir|hk|cn|jp|au|nz)/?\b',
        'htmlesc': r'&#?[a-zšđžčć0-9]+;',
        'tag': xml,
        'mail': r'[\w.-]+@\w+(?:[.-]\w+)+',
        'mention': r'@[a-zšđžčć0-9_]+',
        'hashtag': r'#\w+(?:[.-]\w+)*',
        'emoticon': emoticon,
        'word': word,
        'arrow': r'<[-]+|[-]+>',
        'dot': r'[.!?/]{2,}',
        'space': r'\s+',
        'other': r'(.)\1*',
        'order': (
            'abbrev', 'num', 'url', 'htmlesc', 'tag', 'mail', 'mention', 'hashtag', 'emoticon', 'word', 'arrow', 'dot',
            'space', 'other')
    },

}

# transform abbreviation lists to sets for lookup during sentence splitting
for lang in abbrevs:
    for type in abbrevs[lang]:
        abbrevs[lang][type] = list(set([e.replace('\\.', '.') for e in abbrevs[lang][type]]))

spaces_re = re.compile(r'\s+', re.UNICODE)


def generate_tokenizer(lang):
    token_re = re.compile(r'|'.join([langs[lang][e] for e in langs[lang]['order']]), re.UNICODE | re.IGNORECASE)
    return token_re


def tokenize(tokenizer, paragraph):
    return [(e.group(0), e.start(0), e.end(0)) for e in
            tokenizer.finditer(paragraph.strip())]  # spaces_re.sub(' ',paragraph.strip()))]


def sentence_split(tokens, lang="sr"):
    boundaries = [0]
    for index in range(len(tokens) - 1):
        token = tokens[index][0]
        if token[0] in '.!?…' or (token.endswith('.') and token.lower() not in abbrevs[lang]['N'] and len(token) > 2 and
                                  tokens[index + 1][0][0] not in '.!?…'):
            if tokens[index + 1][0][0].isupper():
                boundaries.append(index + 1)
                continue
            if index + 2 < len(tokens):
                if tokens[index + 2][0][0].isupper():
                    if tokens[index + 1][0].isspace() or tokens[index + 1][0][0] in '-»"\'„':
                        boundaries.append(index + 1)
                        continue
            if index + 3 < len(tokens):
                if tokens[index + 3][0][0].isupper():
                    if tokens[index + 1][0].isspace() and tokens[index + 2][0][0] in '-»"\'„':
                        boundaries.append(index + 1)
                        continue
            if index + 4 < len(tokens):
                if tokens[index + 4][0][0].isupper():
                    if tokens[index + 1][0].isspace() and tokens[index + 2][0][0] in '-»"\'„' \
                            and tokens[index + 3][0][0] in '-»"\'„':
                        boundaries.append(index + 1)
                        continue
        if token[0] in '.!?…':
            if index + 2 < len(tokens):
                if tokens[index + 2][0][0].isdigit():
                    boundaries.append(index + 1)
                    continue
    boundaries.append(len(tokens))
    sents = []
    for index in range(len(boundaries) - 1):
        sents.append(tokens[boundaries[index]:boundaries[index + 1]])
    return sents


def represent_tomaz(sentences, keepspace=False):
    output = []
    for sent in sentences:
        for token, start, end in sent:
            if not token[0].isspace() or keepspace:
                output.append(token)
        output.append("")
    return output


def rel_tokenize(text, keepspace=False):
    tokenizer = generate_tokenizer('sr')
    text = text.rstrip()
    text = text.replace("<", "\n<").replace(">", ">\n")
    text = text.split("\n")
    tokens = []

    for line in text:
        if line.strip() == '':
            continue
        elif re.match(xml, line):
            tokens.append(line)
            continue

        sentences = sentence_split(tokenize(tokenizer, line), 'sr')
        tokens.extend(represent_tomaz(sentences, keepspace))

    return tokens


def gpt_tokenize(text):
    if "$$" in text:
        new = text.split("$$")
    else:
        tokens = rel_tokenize(text, keepspace=True)
        new = []
        last = ""
        for token in tokens:
            if token != " ":
                if last == " ":
                    new.append(last + token)
                else:
                    new.append(token)
            last = token
    return new


tokenizer = generate_tokenizer('sr')


def sentencize(text):
    res = []
    sentences = sentence_split(tokenize(tokenizer, text), 'sr')
    for s in sentences:
        xs = [x[0] for x in s]
        res.append(xs)
    return res
