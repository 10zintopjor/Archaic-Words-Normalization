from cgitb import text
from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer
import re
import sqlite3
import csv
import yaml


def extract_collated(collated_text,archaic_words):
    p = re.compile("\d+\s*<[^>]*>")
    new_collated_text=""
    start_in = 0
    for m in p.finditer(collated_text):
        note = m.group()
        start,end = m.span()
        default_word,index = get_default_word(collated_text,start-1)
        alt_words = get_alternative_words(note,default_word)
        if default_word in archaic_words:
            new_collated_text+=collated_text[start_in:index-1]+alt_words[0]
        else:
            modern_word = check_lekshi_gurkhang(alt_words)
            if modern_word != None:
                new_collated_text+=collated_text[start_in:index-1]+modern_word    
            else:
                new_collated_text+=collated_text[start_in:end]    
        start_in = end+1

    with open("new_test.txt","w") as f:
        f.write(new_collated_text)


def check_lekshi_gurkhang(words):
    a_yaml_file = open("arch_modern.yml")
    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

    for id in parsed_yaml_file:
        for word in words:
            if parsed_yaml_file[id]['archaic'] == word:
                return parsed_yaml_file[id]['modern'][0] # it is list 
            else:
                modern_words = parsed_yaml_file[id]['modern']
                for modern_word in modern_words:
                    if modern_word == word:
                        return word

    return None        


def get_alternative_words(note,default_word):
    words =[]
    print(note)
    regex = "»([^(«|>)]*)"
    texts = re.findall(regex,note)

    for text in texts:
        if text == "":
            continue
        words.append(text)

    return words

    """ if re.search("»«",note):
        text = re.match(".*»(.*)\s*>",note)
        words.append(text.group(1).strip())
    elif re.search("<«.*».*«.*».*>",note):
        text = re.match(".*<«.*»(.*)«.*»(.*)>",note)
        if text.group(1) != text.group(2):
            first_word =text.group(1).strip()
            second_word = text.group(2).strip()
            if first_word != default_word and second_word != default_word:
                words.append(first_word)
                words.append(second_word)
            elif first_word != default_word:
                words.append(first_word)
            elif second_word != None:
                words.append(second_word)
        else:
            words.append(text.group(1).strip())
    elif re.search("<«.*».*>",note):
        text = re.match(".*<«.*»(.*)>",note)
        words.append(text.group(1).strip())  """       


def get_default_word(collated_text,start):
    index = start
    new_index = ""
    while index > 0:
        if collated_text[index] == ":":
            new_index =  index+1
            break
        elif re.search("\s",collated_text[index]):
            index_in = start-1
            while collated_text[index_in] != "་":
                index_in-=1
            new_index = index_in+1
            break
        index-=1

    return collated_text[new_index:start+1],new_index


def extract_db():
    archaic_words = []
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    archaic_word ="བརྡ་རྙིང་།"
    with open("dic.csv","w") as f:
        writer = csv.writer(f)
        for row in cur.execute('SELECT word text,result text FROM table_en_ind'):
            word,desc = row     
            writer.writerow([word,desc])
            if desc and archaic_word in desc:
                archaic_words.append(word)
    con.close()

    return archaic_words


def remove_particles(collated_text):
    
    wt = WordTokenizer()
    tokenized_texts = wt.tokenize(collated_text,split_affixes=True)
    
    particle_free_collated_text = ""

    for tokenized_text in tokenized_texts:
        print(tokenized_text.pos)
        print("*******************")
        if tokenized_text.pos and tokenized_text.pos != "PART":
            particle_free_collated_text+=tokenized_text.text
    
    return particle_free_collated_text

def main():
    collated_text = Path("sample_collated.txt").read_text(encoding="utf-8")
    #archaic_words = extract_db()
    archaic_words = ['བཞི་བྱུང་','ཙམ་བླང་གི']
    collated_text = remove_particles(collated_text)
    print(collated_text)
    #extract_collated(collated_text,archaic_words)


if __name__ == "__main__":
    main()