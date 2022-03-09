from asyncio import start_unix_server
from calendar import c
from pathlib import Path
import re
import sqlite3
import csv
import yaml

def extract_collated(c_text,archaic_words):
    p = re.compile("\d+\s*<[^>]*>")
    new_str=""
    start_in = 0
    #notes = re.findall("\d+\s*<.+>",c_text)
    for m in p.finditer(c_text):
        note = m.group()
        start,end = m.span()
        modern_word = get_modern_word(note)
        index = get_main_word(c_text,start-1)
        main_word = c_text[index:start]
        
        if main_word in archaic_words:
            new_str+=c_text[start_in:index-1]+modern_word
        else:
            in_modern_word = check_lekshi_gurkhang(modern_word)
            if in_modern_word != None:
                new_str+=c_text[start_in:index-1]+in_modern_word    
            else:
                new_str+=c_text[start_in:end]    
        start_in = end+1

    with open("new_test.txt","w") as f:
        f.write(new_str)


def check_lekshi_gurkhang(word):
    a_yaml_file = open("arch_modern.yml")
    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

    for id in parsed_yaml_file:
        if parsed_yaml_file[id]['archaic'] == word:
            return parsed_yaml_file[id]['modern'][0] # it is list 

    return None        


def get_modern_word(note):
    if re.search("»«",note):
        text = re.match(".*»(.*)\s*>",note)
        return text.group(1)
    elif re.search("<«.*».*«.*».*།>",note):
        text = re.match(".*<«.*»(.*)«.*»(.*)>",note)
        if text.group(1) != text.group(2):
            first_word = check_lekshi_gurkhang(text.group(1))
            second_word = check_lekshi_gurkhang(text.group(2))
            if first_word != None:
                return first_word
            elif second_word != None:
                return second_word
            else:
                return text.group(1)+"_"+text.group(2)
        else:
            return text.group(1)

def get_main_word(c_text,start):
    index = start
    while index > 0:
        if c_text[index] == ":":
            return index+1
        elif re.search("\s",c_text[index]):
            index_in = start-1
            while c_text[index_in] != "་":
                index_in-=1
            return index_in+1
        index-=1

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


def main():
    c_text = Path("sample_collated.txt").read_text(encoding="utf-8")
    #archaic_words = extract_db()
    archaic_words = ['བཞི་བྱུང་','ཙམ་བླང་གི']
    extract_collated(c_text,archaic_words)

if __name__ == "__main__":
    main()