import json
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

def filter_by_language(reviews, lang = 'en'):
    relevant_reviews = []
    for review in reviews:
        review_text = review['text']		
        try:
            language = detect(review_text)
            if language == lang:
                relevant_reviews.append(review)
        except LangDetectException:
            pass
    return relevant_reviews