from .verse_ref import bcv_to_verse_ref
from .trigrams import trigrams

def get_rows():
    with open("supermorphgnt.txt") as f:
        for line in f:
            yield line.strip().split()

ROWS = {}
for row in get_rows():
    ROWS[row[0]] = row


if __name__ == "__main__":

    for prev_row, row, next_row in trigrams(get_rows()):
        word = row[8]
        norm = row[9]
        lemma = row[10]

        prev_para = prev_row[2] if prev_row else None
        para = row[2]

        NEW_PARAGRAPH = (prev_para != para)
        WORD_UPPER = (word[0] == word[0].upper())
        NORM_UPPER = (norm[0] == norm[0].upper())
        LEMMA_UPPER = (lemma[0] == lemma[0].upper())

        # print(WORD_UPPER, NORM_UPPER, LEMMA_UPPER, NEW_PARAGRAPH)

        # if (WORD_UPPER, NORM_UPPER, LEMMA_UPPER, NEW_PARAGRAPH) == (False, False, False, True):
        #     print(prev_para, para, row)

        if (WORD_UPPER, NORM_UPPER, LEMMA_UPPER, NEW_PARAGRAPH) == (True, False, False, False):
            START_ID = row[0]
            ID = START_ID
            fail = False
            while ID >= START_ID:
                if ROWS[ID][12] != "None":
                    ID = ROWS[ID][12]
                else:
                    fail = True
                    break
            if fail:
                print("??? ... {} [{}]".format(word, bcv_to_verse_ref(row[1], start=61)))
            else:
                print("{} ({}) ... {} [{}]".format(ROWS[ID][8], ROWS[ID][10], word, bcv_to_verse_ref(row[1], start=61)))
