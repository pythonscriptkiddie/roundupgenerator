from bs4 import BeautifulSoup
import re
import requests
import datetime
import pandas as pd
#from .._db import db as db
#import BTCInput2 as btc
#import ui

#pd.options.display.max_colwidth = 200

DEBUG_MODE = True

def read_text(prompt):
    '''
    Displays a prompt and reads in a string of text.
    Keyboard interrupts (CTRL+C) are ignored
    returns a string containing the string input by the user
    '''
    while True:  # repeat forever
        try:
            result=input(prompt) # read the input
            # if we get here no exception was raised
            if result=='':
                #don't accept empty lines
                print('Please enter text')
            else:
                # break out of the loop
                break
        except KeyboardInterrupt:
            # if we get here the user pressed CTRL+C
            print('Please enter text')
            if DEBUG_MODE:
                raise Exception('Keyboard interrupt')

    # return the result
    return result


def read_number(prompt,function):
    '''
    Displays a prompt and reads in a floating point number.
    Keyboard interrupts (CTRL+C) are ignored
    Invalid numbers are rejected
    returns a float containing the value input by the user
    '''
    while True:  # repeat forever
        try:
            number_text=read_text(prompt)
            result=function(number_text) # read the input
            # if we get here no exception was raised
            # break out of the loop
            break
        except ValueError:
            # if we get here the user entered an invalid number
            print('Please enter a number')

    # return the result
    return result

def read_number_ranged(prompt, function, min_value, max_value):
    '''
    Displays a prompt and reads in a number.
    min_value gives the inclusive minimum value
    max_value gives the inclusive maximum value
    Raises an exception if max and min are the wrong way round
    Keyboard interrupts (CTRL+C) are ignored
    Invalid numbers are rejected
    returns a number containing the value input by the user
    '''
    if min_value>max_value:
        # If we get here the min and the max
        # are wrong way round
        raise Exception('Min value is greater than max value')
    while True:  # repeat forever
        result=read_number(prompt,function)
        if result<min_value:
            # Value entered is too low
            print('That number is too low')
            print('Minimum value is:',min_value)
            # Repeat the number reading loop
            continue 
        if result>max_value:
            # Value entered is too high
            print('That number is too high')
            print('Maximum value is:',max_value)
            # Repeat the number reading loop
            continue
        # If we get here the number is valid
        # break out of the loop
        break
    # return the result
    return result

def read_float(prompt):
    '''
    Displays a prompt and reads in a floating point number.
    Keyboard interrupts (CTRL+C) are ignored
    Invalid numbers are rejected
    returns a float containing the value input by the user
    '''
    return read_number(prompt,float)

def read_int(prompt):
    '''
    Displays a prompt and reads in an integer number.
    Keyboard interrupts (CTRL+C) are ignored
    Invalid numbers are rejected
    returns an int containing the value input by the user
    '''
    return read_number(prompt,int)

def read_float_ranged(prompt, min_value, max_value):
    '''
    Displays a prompt and reads in a floating point number.
    min_value gives the inclusive minimum value
    max_value gives the inclusive maximum value
    Raises an exception if max and min are the wrong way round
    Keyboard interrupts (CTRL+C) are ignored
    Invalid numbers are rejected
    returns a number containing the value input by the user
    '''
    return read_number_ranged(prompt,float,min_value,max_value)

def read_int_ranged(prompt, min_value, max_value):
    '''
    Displays a prompt and reads in an integer point number.
    min_value gives the inclusive minimum value
    max_value gives the inclusive maximum value
    Raises an exception if max and min are the wrong way round
    Keyboard interrupts (CTRL+C) are ignored
    Invalid numbers are rejected
    returns a number containing the value input by the user
    '''
    return read_number_ranged(prompt,int,min_value,max_value)


class Article:
    
    article_months = {1:'January', 2: 'February', 3: 'March', 4: 'April',
                      5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
                      10: 'October', 11: 'November', 12: 'December'}
    #article_months is used to load csv files with the month name instead of a number
    
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
    
    @classmethod
    def from_input(cls, link, category):
        try:
            print('Manual article creation')
            print('Press Ctrl+C to cancel')
            if not link:
                print('No link supplied, manual_add must be followed by link')
                return
                #link=read_text('Article url:' )
            name = read_text('Article title: ')
            year = read_int_ranged('Article year: ', 1, 2100)
            month = read_int_ranged('Article month: ', 1, 12)
            day = read_int_ranged('Article day: ', 1, 31)
            #assert Article.validate_date(day=day,month=month,year=year) == True
            author = read_text('Author: ')
            publication = read_text('Publication: ')
            #category = category
            #if category == None:
            #    print('There is no category with that ID. article NOT added.\n')
            #    return
            #else:
            description = read_text('Description: ')
            return cls(link=link, name=name, year=year, month=month,
                           day=day, author=author, publication=publication,
                           category=category, description=description)
        except Exception as e:
            print(e)
            return
                
            pass
        except KeyboardInterrupt:
            print('Ctrl+C pressed, add article cancelled')
    
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
    
    @classmethod
    def from_input(cls):
        try:
            print('Manual category creation')
            print('Press "." to cancel')
            name = read_text('Category name: ')
            #description = read_text('Description: ')
            return cls(name=name)
        except Exception as e:
            print(e)
            return
        except KeyboardInterrupt:
            print('Ctrl+C pressed, add article cancelled')
    
    def __init__(self, id=0, name=None, articles=[]):
        self.id = id
        self.name = name
        self.articles = articles
        
    def __repr__(self):
        template = "id: {0} name: {1}"
        return template.format(self.id, self.name)