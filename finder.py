import difflib
import re
import pandas as pd
from nltk.stem import PorterStemmer
# nltk.download('punkt')
# nltk.download('stopwords')
stemmer = PorterStemmer()


rows = []
datas = pd.read_csv('data.csv')
data = datas.apply(lambda x: x.astype(str).str.lower())
site_features = datas['text']
list_features = site_features.to_list
img_features = datas['img_text']
print (site_features)
link = datas['link']
loop = 1
suspected_link = []
while loop < 100:
    # this is the input data
    raw_word = input("enter the search word with separated by ,")
    words = raw_word.split(sep=",")
    ipword = []
    op = []
    for word in words:
        stem = stemmer.stem(word)
        ipword.append(stem)
    print(ipword)
    # finding the matched row's index that stores in the indexes
    for word in ipword:
        loop_count = 0
        for row in site_features:
            x = re.search(word,row)
            if x:
                op.append(loop_count)
            loop_count = loop_count + 1

    for word in ipword:
        loop_count = 0
        for row in img_features:
            x = re.search(word,row)
            if x:
                op.append(loop_count)
            loop_count = loop_count + 1



    #for row in site_features:
    #    for word in row:
    #        if word not in ipword:
    #            print(row)
                #op.append(indices)

    print(op)

    for i in op:
        url = link[i]
        if url not in suspected_link:
            suspected_link.append(url)
        print(url)

    df = pd.DataFrame(suspected_link)
    df.to_csv('suspected_links.csv', index=True, header=True, mode='w' )
    loop= loop + 1