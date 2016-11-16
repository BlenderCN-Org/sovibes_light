from newspaper import nlp
from nltk import sent_tokenize, re
from newspaper import Article
from json_utils import update_json_file

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words


def clean_sententce(sentence):
    sentence.replace('GIF','')
    re.sub('pic.twitter.com/\w+', '', sentence)
    return  sentence


def summarize_article(article,vibe_description_file_path):
    try:
        article_url = article['alternate'][0]['href']
        article_title = article['title']

        article_newspaper = Article(article_url)
        article_newspaper.download()
        article_newspaper.parse()
        article_newspaper.nlp()

        text_content = article_newspaper.text
        update_json_file(vibe_description_file_path,'textContent',text_content)

        LANGUAGE = 'english'
        parser = HtmlParser.from_url(article_url, Tokenizer('english'))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        article_summary =[]
        for sentence in summarizer(parser.document,3):
            article_summary.append(sentence._text)


    except:
        print('Error summarizing article')
        return False

    update_json_file(vibe_description_file_path,'summary',article_summary)
    update_json_file(vibe_description_file_path, 'keywords', article_newspaper.keywords)

    return True



