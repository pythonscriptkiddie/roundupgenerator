from bs4 import BeautifulSoup
import re
import requests
import datetime
import pandas as pd

pd.options.display.max_colwidth = 200

class Article:
    
    article_months = {1:'January', 2: 'February', 3: 'March', 4: 'April',
                      5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
                      10: 'October', 11: 'November', 12: 'December'}
    
    @staticmethod
    def validate_date(day, month, year):
        try:
            new_date = datetime.datetime(day=day, month=month, year=year)
            if new_date:
                return True
            else:
                return False
        except ValueError:
            return False
    
    @staticmethod
    def get_title(url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html5lib")
        soup_title = str(soup.title)
        html_stripped_title = Article.remove_html_tags(soup_title)
        return html_stripped_title
    
    @staticmethod
    def get_text(url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html5lib")
        soup_text = str(soup.text)
        return soup_text
    
    @staticmethod
    def clean_title(title, divider):
        original_title = title
        new_title_list = original_title.split(divider)
        if len(new_title_list) > 1:
            new_title = new_title_list[0]
            return new_title
        else:
            new_title = original_title
            return new_title
        
    @staticmethod
    def strip_title(article_title):
        regular_title = article_title
        stripped_vertical_bar = Article.clean_title(article_title, divider='|')
        stripped_hyphen = Article.clean_title(article_title, divider = '-')
        stripped_en_dash = Article.clean_title(article_title, divider = '–')
        stripped_em_dash = Article.clean_title(article_title, divider = '—')
        return regular_title, stripped_vertical_bar, stripped_hyphen, stripped_en_dash, stripped_em_dash
    
    @property
    def regular_title(self):
        return Article.strip_title(self.title)[0]
    
    @property
    def stripped_vertical_bar(self):
        return Article.strip_title(self.title)[1]
    
    @property
    def stripped_hyphen(self):
        return Article.strip_title(self.title)[2]
    
    @property
    def stripped_en_dash(self):
        return Article.strip_title(self.title)[3]
    
    @property
    def stripped_em_dash(self):
        return Article.strip_title(self.title)[4]
    
    @property
    def date_string(self):
        template = '{0}/{1}/{2}'
        return template.format(str(self.month), str(self.day).zfill(2), str(self.year))
    
    
    @staticmethod
    def remove_html_tags(text):
        """Remove html tags from a string"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def __init__(self, id=0, name=None, year=0, month=0,day=0, category=None,
                 link=None, description=None, author=None, publication=None):
        self.id = id
        self.name = name
        self.year = year
        self.month = month
        self.day= day
        self.category = category
        self.link = link
        self.description = description
        self.author = author
        self.publication = publication
        
    def __repr__(self):
        template = 'id:{0}, name:{1}, cat:{2}'
        return template.format(self.id, self.name, self.category)
    
    @property
    def url(self):
        return self.link
    
    @property
    def title(self):
        return self.name
    
    @property
    def month_text(self):
        return Article.article_months[self.month]
    
    @property
    def em_dash_stripped_title(self):
        return 
    
    @property
    def orderedDictFormat(self):
        result = self.__dict__
        return result
    
    @property
    def pdFormat(self):
        return  pd.DataFrame.from_dict(self.orderedDictFormat, orient='index')

class Category:
    def __init__(self, id=0, name=None, articles=[]):
        self.id = id
        self.name = name
        self.articles = articles
        
    def __repr__(self):
        template = "id: {0} name: {1}"
        return template.format(self.id, self.name)