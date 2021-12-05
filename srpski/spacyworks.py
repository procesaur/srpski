import spacy
from spacy.tokens import Doc
from spacy.training.loop import train as trainpos
from spacy.training.initialize import init_nlp
from spacy import util

from pathlib import Path
import os
import sys
from unicodedata import category
from distutils.dir_util import copy_tree
from spacy.cli.convert import _write_docs_to_file
from spacy.tokens._serialize import DocBin
from spacy.training.converters.conllu_to_docs import conllu_to_docs

probability = True
lemmat = False
tokenize = False

chrs = (chr(i) for i in range(sys.maxunicode + 1))
punctuation = set(c for c in chrs if category(c).startswith("P"))
numbers = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ","}


def tag_spacytagger(par_path, text, probability, tokenize=False, lemmat=False, right=False):
    nlp = spacy.load(par_path)
    nlp.max_length = 20000000
    nom = 1
    tags = nlp.meta["labels"]["tagger"]
    sent = "SENT" in tags
    punct = "PUNCT" in tags
    num = "NUM" in tags

    if right:
        nom = -1

    pr = ""
    if probability:
        pr = " 1.0"

    if not isinstance(text, str):
        text = "\n".join(text)

    def custom_tokenizer(text):
        if isinstance(text, str):
            tokens = text.split('\n')
        else:
            tokens = text
        # tokens = list(line for line in tokens if line not in ['\n', '', '\0'])
        for i, token in enumerate(tokens):
            if token in ['\n', '', '\0']:
                tokens[i] = "{{S}}"

        return Doc(nlp.vocab, tokens)

    if not tokenize:
        nlp.tokenizer = custom_tokenizer

    doc = nlp(text)
    tagged_lines = []
    tagger = nlp.get_pipe('tagger')
    scores = tagger.model.predict([doc])

    #original = sys.stdout
    #sys.stdout = open(out_path, 'w', encoding='utf-8')

    for idx, token in (enumerate(doc)):

        if token.text != " " and token.text != "{{S}}":

            if set(token.text).issubset(punctuation) and punct:
                if idx + 1 == len(doc):
                    tokprob = "\tPUNCT" + pr
                else:
                    if doc[idx+nom].text == "{{S}}" and sent:
                        tokprob = "\tSENT" + pr
                    else:
                        tokprob = "\tPUNCT" + pr

            elif set(token.text).issubset(numbers) and num:
                tokprob = "\tNUM" + pr

            else:
                tokprob = '\t' + token.tag_
                if probability:
                    tokprob = ''
                    thisscores = scores[0][idx]
                    for i, score in (enumerate(thisscores)):
                        score = round(score, 4)
                        if score > 0.001 and tagger.labels[i] != '_SP':
                            tokprob = tokprob + '\t' + tagger.labels[i] + ' ' + str(score)

            lemma = ''
            if lemmat:
                lemma = '\t' + token.lemma_

            tagged_lines.append(token.text + tokprob + lemma)

    return tagged_lines
    #sys.stdout = original

def gettagmap(uniqpos):
    tagdic = {}
    for p in uniqpos:
        if 'PUN' in p or 'SENT' in p:
            tagdic[p] = 'PUNCT'
        elif 'ADJ' in p or p == 'A' or 'A:' in p:
            tagdic[p] = 'ADJ'
        elif 'ADP' in p or 'PRE' in p:
            tagdic[p] = 'ADP'
        elif 'ADV' in p:
            tagdic[p] = 'ADV'
        elif 'AUX' in p:
            tagdic[p] = 'AUX'
        elif 'CON' in p:
            tagdic[p] = 'CONJ'
        elif 'DET' in p:
            tagdic[p] = 'DET'
        elif 'INT' in p:
            tagdic[p] = 'INTJ'
        elif 'NOUN' in p or p == 'N' or 'N:' in p:
            tagdic[p] = 'NOUN'
        elif 'NUM' in p:
            tagdic[p] = 'NUM'
        elif 'PAR' in p:
            tagdic[p] = 'PART'
        elif 'PROP' in p:
            tagdic[p] = 'PROPN'
        elif 'PRO' in p:
            tagdic[p] = 'PRON'
        elif 'SCON' in p:
            tagdic[p] = 'SCONJ'
        elif 'SYM' in p:
            tagdic[p] = 'SYM'
        elif 'VERB' in p or p == 'V' or 'V:' in p:
            tagdic[p] = 'VERB'
        elif 'SPA' in p:
            tagdic[p] = 'SPACE'
        else:
            tagdic[p] = 'X'
    return tagdic


def train_spacy(cfgpath, trainpath, devpath, temp, destdir, spacygpu=0):
    if not os.path.isdir(destdir):
        os.mkdir(destdir)
    if not os.path.isdir(temp):
        os.mkdir(temp)

    config = util.load_config(cfgpath, interpolate=False)
    config["paths"]["train"] = trainpath
    config["paths"]["dev"] = devpath
    nlp = init_nlp(config, use_gpu=spacygpu)
    trainpos(nlp, temp, use_gpu=spacygpu, stdout=sys.stdout, stderr=sys.stderr)

    copy_tree(str(temp) + '/model-best', destdir)



def prepare_spacy(conlulines, tempdirs, traindir, devdir):

    conllufile = "\n".join(conlulines)
    dox = [x for x in conllu_to_docs(conllufile, n_sents=10)]
    chunksize = len(dox) * 0.9
    spacy_train = ([])
    spacy_dev = ([])
    for i, doc in enumerate(dox):
        if i < chunksize:
            spacy_train.append(doc)
        else:
            spacy_dev.append(doc)

    concatdocsToFile(spacy_train, Path(traindir))
    concatdocsToFile(spacy_dev, Path(devdir))
    tempdirs.append(traindir)
    tempdirs.append(devdir)


def makeconllu(lst, tagmap):
    # sentences sepparated by a double newline
    # extra carefull with quotes, as we will transform it into JSON
    # word ord number, word, lemma, ud tag, tag, and several empty values that arent necessary
    idx = 1
    for i, line in enumerate(lst):

        if line == "":
            idx = 1
            lst[i] = lst[i] + '\n'
        else:
            la = line.split('\t')
            word = la[0]
            # word = word.replace('"', '||||').replace("'", "|||")
            pos = la[1]
            if len(la) > 2:
                lemma = la[2]
            else:
                lemma = ""
            # lemma = lemma.replace('"', '||||').replace("'", "|||")
            lst[i] = str(idx) + '\t' + word + '\t' + lemma + '\t' + tagmap[pos] + '\t' + pos + '\t_\t_\t_\t_\t_'
            idx += 1
    return lst


def concatdocsToFile (docs, outpath):
    db = DocBin(docs=docs, store_user_data=True)
    data = db.to_bytes()
    _write_docs_to_file(data, outpath, "")
