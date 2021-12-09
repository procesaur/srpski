from srpski.pipeline import *
text = ucitaj("D:/aplikacije/BEaSTagger/data/training/zlatin342k.vrt")
text = promesaj(text, separator="\t\t\t",  header=True)
with open("D:/aplikacije/BEaSTagger/data/training/SrpKor4Tagging", "w", encoding="utf-8") as n:
  n.write(text)
