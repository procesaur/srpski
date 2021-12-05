from srpski.pipeline import *
text = ucitaj("http://jerteh.rs/resursi/SRP18751_MilivanG_GlavaSecera.html")
text = ukloni_xml(text)
tokeni = tokenizuj(text)
text = "\n".join(tokeni)
recenica = text.split("\n\n")[0]
text = tokenizuj(recenica)
lexicon = load("http://jerteh.rs/resursi/recnik_public_UD_lat-20211101.txt")
text = preslovi(text)
text = magija(text, lexicon)
model = ucitaj_model("http://jerteh.rs/resursi/Spacy_UD.zip")
text = tagiraj(text, model)
recnik_lema = lemmas(lexicon)
primer = {k: recnik_lema[k] for k in list(recnik_lema)[:5]}
text = lematizuj(text, recnik_lema)
for token in text:
  print(token)
