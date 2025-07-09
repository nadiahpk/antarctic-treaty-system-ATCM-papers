# I know that some documents are mislabelled with the wrong language,
# and some contain translated portions.
#
# For each document, count the proportion of words that are "recognised"
# by dictionaries of the four languages: English, Spanish, French, and Russian.
# This provides a first check on the language-label accuracy.

import os
from pathlib import Path
import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import get_tokenizer

import pandas as pd
import numpy as np


# parameters
# ---

# location of the data (extracted text files)
data_base = Path(os.environ.get("DATA", "."))

# number of example unknown words to include in CSV
nbr_example_unknown_words = 10

# dictionaries for each of the four languages
# for coverage of most variants
lang_2_dictionary_names = {
    "English": ["en_US", "en_GB"],
    "Spanish": ["es_ES", "es_MX", "es_AR"],
    "French": ["fr_FR"],
    "Russian": ["ru_RU"],
}

# the documents are tagged with their language codes,
# (but these tags might be wrong)
tag_2_language = {
    "_e.txt": "English",
    "_s.txt": "Spanish",
    "_f.txt": "French",
    "_r.txt": "Russian",
    "_x.txt": "English", # my own tag used for one mixed document
}

front_page_words = {
    "ANTARCTIC",
    "TREATY",
    "CONSULTATIVE",
    "CONFERENCE",
    "MEETING",
    "TRAITE",
    "TRAITÉ",
    "SUR",
    "L'ANTARCTIQUE",
    "ANTARCTIQUE",
    "RÉUNION",
    "TRATADO",
    "ANTARTICO",
    "REUNIÓN",
    "REUNION",
    "CONSULTIVA",
    "CONSULTATIVA",
    "ДОГОВОР",
    "ОБ",
    "АНТАРКТИКЕ",
    "КОНСУЛЬТАТИВНОЕ",
    "СОВЕЩАНИЕ",
}
# Add lowercase and title-case versions
front_page_words.update(
    word.lower() for word in front_page_words.copy()
)
front_page_words.update(
    word.title() for word in front_page_words.copy()
)


# english tokenizer will work on most European languages
tokenizer = get_tokenizer("en_US")


# get dictionaries
# ---

lang_2_dictionarys = {
    lang: [enchant.Dict(dictionary_name) for dictionary_name in dictionary_names]
    for lang, dictionary_names in lang_2_dictionary_names.items()
}


# get all files recursively
# ---

txt_paths = [f for f in data_base.rglob("*.txt")]


# for each file, for each word, count the proportion of each language
# ---

# storage
nbr_wordsV = list()
presumptive_languageV = list()
propn_presumptiveV = list()
majority_languageV = list()
propn_englishV = list()
propn_spanishV = list()
propn_frenchV = list()
propn_russianV = list()
propn_unknownV = list()
eg_unknown_wordsV = list()

for txt_path in txt_paths:
    # read in text and tokenise
    text = txt_path.read_text(encoding="utf-8")
    tokens = list(tokenizer(text))
    
    if tokens:
        words, _ = zip(*tokens)
        words = [word for word in words if word not in front_page_words]
    else:
        words = []
    
    nbr_words = len(words)

    # presumptive language
    presumptive_lang = None
    for tag, lang in tag_2_language.items():
        if tag in str(txt_path):
            presumptive_lang = lang
            break
    if presumptive_lang is None:
        presumptive_lang = "English" # just pick something

    if nbr_words > 0:

        lang_2_count = {
            "English": 0,
            "Spanish": 0,
            "French": 0,
            "Russian": 0,
            "unknown": 0,
        }
        nbr_presumptive = 0
        unknown_words = set()

        for word in words:

            # list of every language that identifies word
            word_found_in = list()
            for lang, dictionarys in lang_2_dictionarys.items():
                if any([dictionary.check(word) for dictionary in dictionarys]):
                    word_found_in.append(lang)
            
            if not word_found_in:
                # if it wasn't found in any dictionary, count it as unknown,
                # and save examples
                lang_2_count["unknown"] += 1
                if len(unknown_words) < nbr_example_unknown_words:
                    unknown_words.add(word)
            else:
                # add a count if the presumptive language was found
                if presumptive_lang in word_found_in:
                    nbr_presumptive += 1

                # attribute word to each language proportionally
                propn_attribution = 1 / len(word_found_in)
                for lang in word_found_in:
                    lang_2_count[lang] += propn_attribution

        # identify majority language
        majority_language = max(lang_2_count, key=lang_2_count.get)

        # store
        # ---

        nbr_wordsV.append(nbr_words)
        presumptive_languageV.append(presumptive_lang)
        propn_presumptiveV.append(nbr_presumptive/nbr_words)
        majority_languageV.append(majority_language)
        propn_englishV.append(lang_2_count["English"]/nbr_words)
        propn_spanishV.append(lang_2_count["Spanish"]/nbr_words)
        propn_frenchV.append(lang_2_count["French"]/nbr_words)
        propn_russianV.append(lang_2_count["Russian"]/nbr_words)
        propn_unknownV.append(lang_2_count["unknown"]/nbr_words)
        eg_unknown_wordsV.append(" ".join(unknown_words))

    else:

        # leave most of these empty
        nbr_wordsV.append(nbr_words)
        presumptive_languageV.append(presumptive_lang)
        propn_presumptiveV.append(0)
        majority_languageV.append("")
        propn_englishV.append(0)
        propn_spanishV.append(0)
        propn_frenchV.append(0)
        propn_russianV.append(0)
        propn_unknownV.append(0)
        eg_unknown_wordsV.append("")



# write info to a CSV
# ---

txt_rel_paths = [path.relative_to(data_base) for path in txt_paths]
df = pd.DataFrame(
    {
        "path": txt_rel_paths,
        "nbr_words": nbr_wordsV,
        "presumptive_language": presumptive_languageV,
        "propn_presumptive": propn_presumptiveV,
        "majority_language": majority_languageV,
        "propn_english": propn_englishV,
        "propn_spanish": propn_spanishV,
        "propn_french": propn_frenchV,
        "propn_russian": propn_russianV,
        "propn_unknown": propn_unknownV,
        "example_unknown_words": eg_unknown_wordsV,
    }
)

# I will go through each with a large number of spelling errors and indicate their language
df.to_csv("../results_describe_data/count_languages.csv", index=False)
