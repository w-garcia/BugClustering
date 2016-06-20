import nltk as nlp
from nltk.book import *

functions = {text1: "1",
             text2: "2",
             text3: "3",
             text4: "4",
             text5: "5",
             text6: "6",
             text7: "7",
             text8: "8",
             text9: "9"}
while (True):
    num = raw_input("Which text? ")
    text = raw_input("What text?")
    if num is 0:
        "Exit."
        break
    for key, val in functions.items():
        if val == num:
            key.concordance(text)
