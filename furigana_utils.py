import pykakasi
import json
import unicodedata
from sudachipy import Dictionary, SplitMode

# Returns True if the word doesn't contain any kanji, hiragana or katakana
# characters, False otherwise. Japanese punctuation still returns True.
def is_latin_or_symbol(word: str):
    for char in word:
        unicode_category = unicodedata.category(char)
        if(unicode_category.startswith('Lo') or    # Kanji
        unicode_category.startswith('Hiragana') or # Hiragana
        unicode_category.startswith('Katakana')):  # Katakana
            return False
    return True

def get_furigana(text: str):

    # Initialize SudachiPy.
    tokenizer = Dictionary().create()
    # Tokenize the text.
    morphemes = tokenizer.tokenize(text, SplitMode.C)

    # Initialize kakasi to convert text to hiragana.
    kakasi = pykakasi.kakasi()
    kakasi.setMode("K", "H")
    conv = kakasi.getConverter()

    # The list of words to return.
    wordsList = []

    for morph in morphemes:
        # Convert writing and reading to hiragana to make them easily comparable.
        writing = str(conv.do(morph.surface()))
        reading = str(conv.do(morph.reading_form()))

        # If the morphem does not contain any kanji, hiragana or katana, 
        # then add it to the list as is.
        if is_latin_or_symbol(writing) or writing == reading:
            if morph.surface() == ' ': # If it is a space
                wordsList.append(['　']) # Replace it with ideographic spaces.
            else:
                wordsList.append([morph.surface()]) #Otherwise just add the word to the list as is.

        # If it is a japanese word, apply the following algorythm. This is based on the fact that the
        # kanji are usually at the start of the words. This assumption works pretty well most of the time,
        # even if in some rare cases, when words have kanji, then hiragana, then kanji again, like in the
        # word '捜し物', also the し will be included in the furigana. It is not perfect but it doesn't create
        # any problem.
        else:
            same = '' # The part of the words that is common to writing and reading (can be  empty).
            kanji = '' # The string containing the writing of this word.
            hiragana = '' # The string containing the reading of this word.

            #Start from the end of the words
            wIndex = len(writing)-1
            rIndex = len(reading)-1
            ended = False
            # Go back while they have the same characters
            while not ended:
                wChar = writing[wIndex]
                rChar = reading[rIndex]
                # If the characters at the given indexes are the same, add it to the front of the common string.
                if wChar == rChar:
                    same = wChar + same
                # Otherwise, from 0 to the current indexes, we have:
                else:
                    ended = True
                    kanji = writing[0:wIndex+1] # The kanji writing (base for the furigana).
                    hiragana = reading[0:rIndex+1] # The hiragana reading (the actual furigana).

                # Decrease the indexes
                wIndex = wIndex - 1
                rIndex = rIndex -1


            # Add the kanji + optional hiragana to the list.
            wordsList.append([kanji, hiragana])
            # If there was a common ending of writing and reading, add it after the furigana part.
            if len(same) > 0:
                wordsList.append([same])


    # Encode the list as Json.
    encoded = json.dumps(wordsList, ensure_ascii=False)

    # I'm sure there's a better way to do it, but for now this is the only method I found
    # to output japanese in plain text instead of bytes or u-escaped (\u) values.
    plain_text_json = encoded.encode("utf8").decode()

    return plain_text_json