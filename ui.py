#!/usr/bin/env/python3

'''
5/22/19 - Get article titles using BeautifulSoup
'''

import _db.db as db
from objects.objects import Article, Category
import rd.roundup_docx as roundup_docx
import btc.BTCInput as btc
import operator
import time
import csv
import glob
import cmd
import sys
import news.news_article as na


'''perhaps create a menu that appears when you choose the edit article option
then gives you choice of what to edit'''

        
def display_menu(title, menu_items, end='   '):
    print(title.upper())
    for i in menu_items:
        print(i, end=end)

def display_categories(command=''):
    del command
    print("CATEGORIES")
    categories = db.get_categories()    
    for category in categories:
        print(str(category.id) + ". " + category.name.strip(), end='   ')
    print()

def display_single_article2(article, title_term=''):
    print(article.pdFormat)

def display_single_article(article, title_term):
    template ='''
ARTICLE ID - {0}\tARTICLE TITLE: {1}
AUTHOR: {2}\tPUBLICATION: {3}'''
    

    print(template.format(title_term, article.title, article.author, article.publication))
    print("-" * 155)
    template2 = "Category: {0}\nDate: {1}\nDescription: {2}\nLink: {3}"

    print(template2.format(article.category.name, article.date_string,
                                 article.description, article.link))  
    print()

    
def display_articles(articles, title_term):
    print("ARTICLES - " + title_term)
    line_format = "{0:3s} {1:50s}\t{2:10s} {3:10}\t{4:35s} {5:35s}"
    print(line_format.format("ID", "Name", "Category", 'Date', "Description","Link"))
    print("-" * 155)
    for article in articles:
        print(line_format.format(str(article.id), article.name.lstrip()[:50],
                                 article.category.name[:10], article.date_string,
                                 article.description[:35], article.link[:35]))                          
    print()

def display_articles_by_name():
    title_snippet = btc.read_text('Enter article title or "." to cancel: ')
    if title_snippet != '.':
        result = db.display_article_by_name(title_snippet)
        if result == None:
            print('There is no article with that name.\n')
        else:
            display_single_article(result, str(result.id))
    else:
        print('Search cancelled, returning to main menu.')

def display_articles_by_category_id(category_id):
    category = db.get_category(category_id)
    if category == None:
        print("There is no category with that ID.\n")
    else:
        print()
        articles = db.get_articles_by_category_id(category_id)
        display_articles(articles, category.name.upper())
        print('Total articles: {0}'.format(db.get_article_count(category_id)))

def display_articles_by_category_name(category_snippet):
    search_category = db.get_category_by_name(category_snippet)
    if search_category == None:
        print('There is no category with that ID.\n')
    else:
        print()
        search_category_id = search_category.id
        articles = db.get_articles_by_category_id(search_category_id)
        display_articles(articles, search_category.name.upper())
  
def date_search():
    search_choice = btc.read_int_ranged('Options:\n1 - day\n2 - month\n3 - year\n4 - cancel\nEnter your choice: ', 1, 4)
    if search_choice in range(1, 4): #user searches by year
        year = btc.read_int('Year: ')
        if search_choice in range(1, 3):
            month = btc.read_int('Month: ')
            if search_choice in range(1, 2):
                day = btc.read_int('Day: ')
                if Article.validate_date(day=day, month=month, year=year) == True:
                    display_articles_by_date(year, month, day)
                else:
                    print('Invalid date selected')
            else:
                display_articles_by_month(month, year)
        else:
            display_articles_by_year(year)
    else:
        print('Search cancelled. ')
    
      
def display_articles_by_year(year):
    print()
    articles = db.get_articles_by_year(year)
    display_articles(articles, str(year))

def display_articles_by_month(month, year):
    print()
    articles = db.get_articles_by_month(month, year)
    display_articles(articles, "MONTH: " + str(month))
    
def display_articles_by_date(year, month, day):
    articles = db.get_articles_by_date(day, month, year)
    display_articles(articles, "DATE: {0}/{1}/{2}".format(month, day, year))
    
def display_article_by_id():
    article_id = int(input("Article ID: "))
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        
def display_articles_by_author():
    author_snippet = btc.read_text("Author Name: ")
    articles = db.display_articles_by_author(author_snippet)
    if articles == None:
        print("There are no articles by that author. article NOT found.\n")
    else:
        print()
        #display_single_article(article, str(article.id))
        display_articles(articles, "AUTHOR: " + str(articles[0].author))

def display_articles_by_publication():
    publication_snippet = btc.read_text("Publication: ")
    publications = db.display_articles_by_publication(publication_snippet)
    if publications == None:
        print("There are no articles by that publication. article NOT found.\n")
    else:
        print()
        display_articles(publications, "PUBLICATION: " + str(publications[0].publication))

def add_article_from_newspaper(link):
    '''
    Adds an article from the newspaper module after downloading it
    '''
    try:
        #link = btc.read_text('Link or "." to cancel: ')
        #try:
        newNewsItem = na.get_article_from_url(link)
        print(newNewsItem)
        #except Exception as e:
            #print(e)
            #get article title
        
        name = newNewsItem.title #get the title for the article
        print('NameTest {0}'.format(name))
            #get article author
        author = ' '.join(newNewsItem.authors)
            #get article publication
        publication = newNewsItem.meta_data['og']['site_name']
        year = newNewsItem.publish_date.year
        month = newNewsItem.publish_date.month
        day = newNewsItem.publish_date.day
            
        summary = newNewsItem.summary
        keywords = ', '.join(newNewsItem.keywords)
        print(name)
        print(author)
        print(publication)
        print('{0}/{1}/{2}'.format(month, day, year))
        print(summary)
        print(keywords)
        display_categories()
        category_id = btc.read_text("Category ID: ")
        category = db.get_category(category_id)
        if category == None:
            print('There is no category with that ID. article NOT added.\n')
            return
        description_choice = btc.read_text('View article description? y/n: ')
        if description_choice == 'y':
            print(name)
            print(summary)
            print(keywords)
        description = btc.read_text("Description or '.' to cancel: ")
        if description == ".":
            return
        else:
            article = Article(name=name, year=year, month=month,day=day,
                      category=category, link=link, description=description,
                      author=author, publication=publication)
        db.add_article(article)    
        print(name + " was added to database.\n")
    except Exception as e:
        print('Article download failed.', e)
    #new_article = Article(link=)
    #print('Article download failed. Return to main menu.')

def add_article():
    #ask for link of article first:
    link = btc.read_text('Link or "." to cancel: ')
    if link == '.':
        return
    try:
        proposed_title = Article.get_title(link)
        print('Proposed title: {0}'.format(proposed_title))
    except:
        print('Unable to scrape title')
        proposed_title = 'Scraping error'
    title_choice = btc.read_float_ranged(prompt='Press 1 to accept title, 2 to enter different title: ',
                                         min_value=1, max_value=2)
    if title_choice == 1:
        name = proposed_title
    else:
        name = btc.read_text('Enter name or "." to cancel: ')
        if name == '.':
            return
    author = btc.read_text('Enter author or "." to cancel: ')
    publication = btc.read_text('Enter publication or "." to cancel: ')
    
    #name        = input("Name: ")
    year      = btc.read_int_ranged('Year: ', min_value = -1, max_value = 2030)
    month     = btc.read_int_ranged('Month: ', min_value = -1, max_value = 12)
    day       = btc.read_int_ranged('Day: ', min_value = -1, max_value = 31)
    print()
    display_categories()
    category_id = btc.read_text("Category ID: ")
    category = db.get_category(category_id)
    if category == None:
        print('There is no category with that ID. article NOT added.\n')
    #ategory_id = int(input("Category ID: "))
    #link = input("Link: ")
    else:
        description_choice = btc.read_text('View article description? y/n: ')
        if description_choice == 'y':
            article_summary = na.get_article_summary(link)
            print(article_summary)
            #article_text = Article.get_text(link)
            #article_text = dm.get_cleaned_text(link)
            #article_text = article_text.split()
            #article_text = [i for i in article_text if de.isEnglish(i) == True]
            #article_text = ' '.join(article_text)
            print(article_summary)
        description = btc.read_text("Description or '.' to cancel: ")
        if description == ".":
            return
        else:
            article = Article(name=name, year=year, month=month,day=day,
                      category=category, link=link, description=description,
                      author=author, publication=publication)
        db.add_article(article)    
        print(name + " was added to database.\n")



def update_article_name(article_id):
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to edit article title, 2 to leave as is: ' ,
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            new_title = btc.read_text('Enter new title or . to cancel: ')
            if new_title != '.':
                db.update_article_name(article_id, new_title)
        else:
            print('Edit cancelled, article title unchanged')
            
def update_article_category(article_id):
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to edit article category, 2 to leave as is: ' ,
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            new_category_id = btc.read_int('Enter new category_id: ')
            result = db.get_category(new_category_id)
            if result == None:
                print('There is no category with that ID, article category NOT updated.\n')
            else:
                db.update_article_category(article_id, new_category_id)
        else:
            print('Edit cancelled, article title unchanged')
            
def update_article_description(article_id):
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to edit article description, 2 to leave as is: ' ,
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            description_choice = btc.read_text('View article description? y/n: ')
            if description_choice == 'y':
                article_summary = na.get_article_summary(article.link)
                print(article_summary)
#                article_text = Article.get_text(article.link)
#                #article_text = dm.get_cleaned_text(link)
#                article_text = article_text.split()
#                article_text = [i for i in article_text if de.isEnglish(i) == True]
#                article_text = ' '.join(article_text)
#                print(article_text)
            new_description = btc.read_text('Enter new description or "." to cancel: ')
            
            if new_description != '.':
                db.update_article_description(article_id, new_description)
                print('Article description updated.\n')
            else:
                print('Edit cancelled, article description unchanged')
        else:
            print('Edit cancelled, article description unchanged')

def update_article_author(article_id):
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to edit article author, 2 to leave as is: ' ,
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            new_author = btc.read_text('Enter new author name or . to cancel: ')
            if new_author != '.':
                db.update_article_author(article_id, new_author)
        else:
            print('Edit cancelled, article title unchanged')

def update_article_publication(article_id):
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to edit article publication, 2 to leave as is: ' ,
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            new_publication = btc.read_text('Enter new publication name or . to cancel: ')
            if new_publication != '.':
                db.update_article_publication(article_id, new_publication)
                print(article_id, new_publication)
        else:
            print('Edit cancelled, article title unchanged')

def update_article_date(article_id):
    article = db.get_article(article_id)
    if article == None:
        print("There is no article with that ID. article NOT found.\n")
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to edit article date, 2 to leave as is: ' ,
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            new_day = btc.read_int_ranged('Enter new day: ', min_value = 1, max_value = 31)
            new_month = btc.read_int_ranged('Enter new month: ', min_value = 1, max_value = 12)
            new_year = btc.read_int_ranged('Enter new year: ', min_value = 1, max_value = 2100)
            date_choice = btc.read_int_ranged('1 to change date to: {0}/{1}/{2}, 2 to cancel: '.format(new_month, new_day, new_year),
                                              min_value=1, max_value=2)
            if date_choice == 1:
                db.update_article_date(article_id, new_day, new_month, new_year)
                print('Update complete.\n')
            elif date_choice == 2:
                print('Edit cancelled, article date unchanged')
        else:
            print('Edit cancelled, article date unchanged')

def scrape_article_name(article_id):
    article = db.get_article(article_id)
    if article == None:
        print('There is no article with that ID. article NOT found.\n')
    else:
        print()
        display_single_article(article, str(article.id))
        article_choice = btc.read_int_ranged('1 to rescrape title, 2 to leave as is: ',
                                             min_value = 1, max_value = 2)
        if article_choice == 1:
            try:
                new_title = Article.get_title(article.link)
                print('''
New title: {0}
Old title: {1}'''.format(new_title, article.name))
            except:
                new_title = 'Title scrape failed'
            title_choice = btc.read_int_ranged('1 to replace title, 2 to keep original title: ',
                                               min_value = 1, max_value = 2)
            if title_choice == 1:
                db.update_article_name(article_id, new_title)
            elif title_choice == 2:
                print('article update cancelled')
        elif article_choice == 2:
            print('article update cancelled')
    
def finalize_article_descriptions(month, year=2019):
    undescribed = db.finalize_descriptions(month, year)
    undescribed_articles = len(undescribed)
    print('{0} undescribed articles'.format(undescribed_articles))
    for article in undescribed:
        print('{0} undescribed articles2'.format(undescribed_articles))
        update_article_description(article.id)
        description_choice = btc.read_int_ranged('{0} descriptions remaining. Press 1 to continue, 2 to cancel: '.format(undescribed_articles), 1, 2)
        if description_choice == 2:
            print('Update descriptions cancelled')
            break
        
def finalize_title_stripping(month, year):
    articles = db.get_articles_by_month(month=month, year=year)
    articles_remaining = len(articles)
    for article in articles:
        print('{0} articles remaining'.format(articles_remaining))
        display_single_article(article, title_term = article.id)
        strip_choice = btc.read_int_ranged('1 to strip article, 2 to skip, 3 to return to main menu: ', 1, 3)
        if strip_choice == 1:
            strip_article_title(article.id)
            articles_remaining -= 1
        if strip_choice == 2:
            articles_remaining -= 1
            print('Article title unchanged.')
        if strip_choice == 3:
            print('strip titles cancelled')
            #display_title()
            break
            

def get_monthly_category_stats(month, year):
    categories = db.get_categories()
    total_articles = len(db.get_articles_by_month(month, year))
    category_ids = [[category.id, category.name, db.get_monthly_article_count(category.id, month, year)] for category in categories]
    category_ids = sorted(category_ids, key=operator.itemgetter(2), reverse=True)
    uncategorized_articles = db.display_articles_by_description('Not specified')
    uncategorized_articles = len(uncategorized_articles)
    try:
        percent_incomplete = (uncategorized_articles/total_articles)*100
        total_articles_completed = 100
        percent_incomplete = total_articles_completed - percent_incomplete
        print('CATEGORY STATS')
        print('-'*64)
        line_format = '{0:<3} {1:11s} \t{2:10}'
        print('{0:<3} {1:11s} {2:10}'.format('ID', 'Name', '\tQty.'))
        print('-'*64)
        for item in category_ids:
            print(line_format.format(item[0], item[1], str(item[2])))
        print('-'*64)
        print('Uncategorized Articles: {0} (Completed: {1} percent)'.format(uncategorized_articles, percent_incomplete))
        print('Total Articles: {0}'.format(total_articles))
    except ZeroDivisionError as e:
        print(e)
        return

def get_yearly_category_stats(year):
    categories = db.get_categories()
    total_articles = len(db.get_articles_by_year(year))
    category_ids = [[category.id, category.name, db.get_yearly_article_count(category.id, year)] for category in categories]
    category_ids = sorted(category_ids, key=operator.itemgetter(2), reverse=True)
    uncategorized_articles = db.display_articles_by_description('Not specified')
    uncategorized_articles = len(uncategorized_articles)
    try:
        percent_incomplete = (uncategorized_articles/total_articles)*100
        total_articles_completed = 100
        percent_incomplete = total_articles_completed - percent_incomplete
        print('CATEGORY STATS - {0}'.format(year))
        print('-'*64)
        line_format = '{0:<3} {1:11s} \t{2:10}'
        print('{0:<3} {1:11s} {2:10}'.format('ID', 'Name', '\tQty.'))
        print('-'*64)
        for item in category_ids:
            print(line_format.format(item[0], item[1], str(item[2])))
        print('-'*64)
        print('Uncategorized Articles: {0} (Completed: {1} percent)'.format(uncategorized_articles, percent_incomplete))
        print('Total Articles: {0}'.format(total_articles))
    except ZeroDivisionError as e:
        print(e)
        return
    
def get_category_id(category_name):
    '''Takes the category name and returns the category ID'''
    #category_name = btc.read_text("Enter category ID or name: ")
    new_category = db.get_category_by_name(category_name)
    category_id = new_category.id
    return category_id
    
def get_csv_in_directory():
    file_list = glob.glob('*.csv')
    print('Files available: ')
    for item in file_list:
        print(item, end='\n')
    #try:
    importing_file_name = btc.read_text('Enter filename from the list or ". " to cancel: ')
    if importing_file_name != '.':
        filename='{0}.csv'.format(importing_file_name)
        csv_articles = create_csv_list(filename)
        print(csv_articles)
        #csv_articles = [csv_item_to_article(csv_article) for csv_article in csv_articles]
        print('Articles to import:')
        try:
            for article in csv_articles:
                try:
                    csv_article = csv_item_to_article(article)
                    try:
                        csv_article.name = Article.get_title(csv_article.link)
                    except Exception as e:
                        print(e)
                        csv_article.name = 'Not specified'
                    db.add_article_from_csv(csv_article)
                    print(csv_article.name + " was added to database.\n")
                #print('Import complete, return to main menu \n')
                except Exception as e:
                    print(e)
                    print('Article import failed.')
                    continue
            print('Import complete, return to main menu')
        except Exception as e:
            print(e)


def create_csv_list(filename):
    csvRows = []
    csvFileObj = open(filename)
    readerObj = csv.reader(csvFileObj)
    print('csv reader created')
    for row in readerObj:
        if readerObj.line_num == 1:
            continue
        csvRows.append(row)
    csvFileObj.close()
    print('csv list created')
    return csvRows

    
def csv_item_to_article(csv_list_item):
    new_article_link = csv_list_item[0]
    new_article_category = get_category_id(csv_list_item[1])
    new_article_day = csv_list_item[2]
    new_article_month = csv_list_item[3]
    new_article_year = csv_list_item[4]
    article_from_csv = Article(name='Untitled Article', year=new_article_year, month=new_article_month,day=new_article_day,
                      category=new_article_category, link=new_article_link, description='Not specified',
                      author='Not specified', publication='Not specified')
    return article_from_csv

def strip_article_title(article_id):
    #article_id = btc.read_int("article ID: ")
    article = db.get_article(article_id)
    if article == None:
        print('There was no article with that ID. Article NOT found.\n')
    else:
        print("1 -",article.regular_title, 'original title')
        print("2 -",article.stripped_vertical_bar)
        print("3 -",article.stripped_em_dash)
        print("4 -",article.stripped_en_dash)
        print("5 -",article.stripped_hyphen)
        title_choice = btc.read_int_ranged('Select the best version of the title or "." to cancel: ',
                                       min_value=1, max_value=5)
        if title_choice == 1:
            print('Original title maintained, returning to main menu')
        elif title_choice == 2:
            db.update_article_name(article_id, article.stripped_vertical_bar)
            print('Update complete')
        elif title_choice == 3:
            db.update_article_name(article_id, article.stripped_em_dash)
            print('Update complete')
        elif title_choice == 4:
            db.update_article_name(article_id, article.stripped_en_dash)
            print('Update complete')
        elif title_choice == 5:
            db.update_article_name(article_id, article.stripped_hyphen)
            print('Update complete')
            

def delete_article(article_id):
    #article_id = int(input("article ID: "))
    article = db.get_article(article_id)
    choice = input("Are you sure you want to delete '" + 
                   article.name + "'? (y/n): ")
    if choice == "y":
        db.delete_article(article_id)
        print("'" + article.name + "' was deleted from database.\n")
    else:
        print("'" + article.name + "' was NOT deleted from database.\n")

def add_category():
    category_name = btc.read_text('Enter the category name or . to cancel: ')
    if category_name != '.':
        new_category = Category(name=category_name)
        db.add_category(new_category)

        
def update_category(category_id=0):
    if category_id == 0:
        category_id = int(input("category ID: "))
    category = db.get_category(category_id)
    articles = db.get_articles_by_category_id(category_id)
    display_articles(articles, category.name.upper())
    new_category_name = btc.read_text("Enter new category name or '.' to cancel: ")
    if new_category_name != '.':
        update_choice = btc.read_int_ranged("1 to change article name to {0}, 2 to cancel: ".format(new_category_name),
                                            1, 2)
        if update_choice == 1:
            db.update_category(category_id, new_category_name)
            print('Category update complete\n')
        elif update_choice == 2:
            print('Update cancelled.\n')

def delete_category():
    category_id = int(input("category ID: "))
    articles_in_category = db.get_articles_by_category_id(category_id)
    if len(articles_in_category) > 0:
        print('Category contains articles, cannot be deleted')
    elif len(articles_in_category) == 0:
        delete_choice = btc.read_float_ranged('Press 1 to delete, 2 to cancel: ', 1, 2)
        if delete_choice == 1:
            db.delete_category(category_id)
            print('Category deleted.\n')
        elif delete_choice == 2:
            print('Delete cancelled, returning to category menu')

def export_roundup():
    roundup_title = btc.read_text('Enter the roundup title or "." to cancel: ')
    filename = btc.read_text('Enter the filename or "." to cancel: ')
    if roundup_title != '.':
        roundup_categories = db.get_categories()
        for category in roundup_categories:
            category.articles = db.get_articles_by_category_id(category.id)
        roundup_docx.create_complete_roundup(filename=filename, roundup_title=roundup_title, categories=roundup_categories)
        
def export_roundup_by_month():
    roundup_title = btc.read_text('Enter the roundup title: ')
    roundup_month = btc.read_int_ranged('Enter roundup month: ', 1, 12)
    roundup_year = btc.read_int_ranged('Enter roundup year: ', 1, 2100)
    filename = btc.read_text('Enter roundup filename: ')
    roundup_choice = btc.read_int_ranged('Enter 1 to export roundup, 2 to cancel: ', 1, 2)
    if roundup_choice == 1:
        roundup_categories = db.get_categories()
        for category in roundup_categories:
            category.articles = db.get_articles_for_roundup(roundup_month, roundup_year, category.id)
        roundup_docx.create_complete_roundup(filename=filename, roundup_title=roundup_title, categories=roundup_categories)
        #display_title()
    elif roundup_choice == 2:
        print('Roundup export cancelled. Return to main menu.\n')
        #display_title()
        
def export_roundup_by_year():
    roundup_title = btc.read_text('Enter the roundup title: ')
    roundup_year = btc.read_int_ranged('Enter roundup year: ', 1, 2100)
    filename = btc.read_text('Enter roundup filename: ')
    roundup_choice = btc.read_int_ranged('Enter 1 to export roundup, 2 to cancel: ', 1, 2)
    if roundup_choice == 1:
        roundup_categories = db.get_categories()
        for category in roundup_categories:
            category.articles = db.yearly_roundup_articles(roundup_year, category.id)
        roundup_docx.create_complete_roundup(filename=filename, roundup_title=roundup_title, categories=roundup_categories)
        #display_title()
    elif roundup_choice == 2:
        print('Roundup export cancelled. Return to main menu.\n')
        #display_title()
        
def export_roundup_by_category():
    display_categories()
    roundup_categories = db.get_categories()
    categories_remaining = len(roundup_categories)
    categories_for_roundup = []
    for category in roundup_categories:
        print('Categories remaining: {0}'.format(categories_remaining))
        print('Include {0}'.format(category.name))
        category_choice = btc.read_int_ranged('1 to include, 2 to exclude: ', 1, 2)
        if category_choice != 1:
            categories_for_roundup.append(category)
    roundup_title = btc.read_text('Enter the roundup title: ')
    roundup_month = btc.read_int_ranged('Enter roundup month: ', 1, 12)
    roundup_year = btc.read_int_ranged('Enter roundup year: ', 1, 2100)
    filename = btc.read_text('Enter roundup filename: ')
    roundup_choice = btc.read_int_ranged('Enter 1 to export roundup, 2 to cancel: ', 1, 2)
    if roundup_choice == 1:
        for category in categories_for_roundup:
#        for category in roundup_categories:
            category.articles = db.get_articles_for_roundup(roundup_month, roundup_year, category.id)
        roundup_docx.create_complete_roundup(filename=filename, roundup_title=roundup_title, categories=categories_for_roundup)
        #display_title()
    elif roundup_choice == 2:
        print('Roundup export cancelled. Return to main menu.\n')
        #display_title()

    
            
def add_article_interface(command):
    add_commands = {'new': add_article,
                    'import': get_csv_in_directory}
                      
    if not command:
        print('Enter command')
    else:
        try:
            command=add_commands[command]()
        except KeyError:
            print('Invalid suffix for add')



def search_article_interface(command):
    search_commands = {'id': display_article_by_id,
                       'name': display_articles_by_name,
                       'author' : display_articles_by_author,
                       'category': get_articles_by_category,
                       'publication': display_articles_by_publication,
                       'date': date_search,
                       }
    
    if not command:
        print('Enter command')
    else:
        try:
            command=search_commands[command]()
        except KeyError:
            print('Invalid suffix for search')
        except IndexError as e:
            print('Publication not found error code:', e)

    

def get_articles_by_category():
    category = btc.read_text("Enter category name or number here:  ")
    if category.isalpha() == True:
        display_articles_by_category_name(category)
    elif category.isnumeric() == True:
        try:
            category_id = int(category)
            display_articles_by_category_id(category_id)
            
        except:
            print('Article search cancelled. Return to main menu.\n')
         


category_menu = ['add_cat - Add a category', 'update_cat - Update category name',
                 'del_cat - delete category', 'cat_help - display categories']

def category_interface(command):
    category_commands = {'add': add_category,
                       'update': update_category,
                       'display': display_categories,
                       'delete' : delete_category,
                       'stats': get_articles_by_category,
                       }
    
    if not command:
        print('Enter command')
    else:
        try:
            command=category_commands[command]()
        except KeyError:
            print('Invalid suffix for category menu')


def export_interface(command):
    export_commands = {'month': export_roundup_by_month, 'category' : export_roundup_by_category}
    
    if not command:
        print('Enter command')
    else:
        try:
            command=export_commands[command]()
        except KeyError:
            print('Please enter a valid parameter for "export"')


def get_stats():
    stats_choice = btc.read_int_ranged('1 - monthly stats; 2 - yearly stats; 3 - main menu: ',
                                       1, 3)
    if stats_choice in range(1, 3):
        year = btc.read_int_ranged('Enter article year: ', 1, 2100)
        if stats_choice in range(1, 2):
            month = btc.read_int_ranged('Enter article month: ', 1, 12)
            get_monthly_category_stats(month, year)
        else:
            get_yearly_category_stats(year)
    else:
        time.sleep(0.25)
        print('Returning to main menu.\n')
        time.sleep(0.25)
    
def split_command(command):
    if type(command) != int:
        split_command = command.split(' ')
        return split_command[0], split_command[1]
    else:
        print('Invalid command: please enter with format finalize [m] [y]')

class RGenCMD(cmd.Cmd):
        
    intro = "Welcome to RoundupGenerator 3.0"
    prompt = "(RoundupGenerator) "
    entry = ""
    
    def do_search(self, command):
        #command = input('Enter command: ')
        search_article_interface(command)
    
    def help_search(self):
        print('''Enter "search [option]" to search articles: 
search id - search by article id
search name - search by article title
search author - search by author
search category - search by category
search date - search by date''')
        
    def do_add(self, command):
        add_article_interface(command)
        
    def help_add(self):
        print('''Enter add [option] to add articles:
add new - takes input and creates a new article
add import - imports articles from a csv file''')
            
    def do_getfromnews(self, command):
        add_article_from_newspaper(link=command)
    
    def help_getfromnews(self, command):
        print('getfromnews [article_url] creates an article from the newspaper module')
        print('user will be prompted to supply category and description')
        
    def do_udname(self, command):
        update_article_name(article_id = command)
    
    def help_udname(self):
        print('udname [article_id] updates the name of an article')
        print('example: udname 18 \tupdates article id 18')
        
    def do_udartcat(self, command):
        #We pass the article ID to the other function as a command
        update_article_category(article_id = command)
        
    def help_udartcat(self):
        print('udartcat [article_id] updates the category of an article')
        print('example: udartcat 12 \tupdates the category for article id 12')
        
    def do_udartdesc(self, command):
        update_article_description(article_id=command)
        
    def help_udartdesc(self):
        print('udartdesc [article_id] updates the description of an article')
        print('example: udartcat 13 \t updates the description for article id 13')
        
    def do_udartpub(self, command):
        update_article_publication(article_id=command)
        
    def help_udartpub(self):
        print('udartpub [article_id] updates an article\'s publication')
        print('Note: this does not affect other articles from the same publication')

    def do_udartdate(self, command):
        update_article_date(article_id = command)
        
    def help_udartdate(self):
        print('udartdate [article_id] updates the date of an article')
        print('The function calls a prompt for the user to enter the date')
        
    def do_rescrape(self, command):
        scrape_article_name(article_id=command)
        
    def help_rescrape(self):
        print('rescrape [article_id]')
        print('e.g. rescrape 18')
        print('Uses BeautifulSoup to re-scrape the article\'s title')
        
    def do_striptitle(self, command):
        strip_article_title(article_id=command)
        
    def help_striptitle(self):
        print('striptitle [article_id]')
        print('e.g. striptitle 13')
        print('Lets the user remove publication names from the article title')
        print('Publication titles are split using a separator')
        
    def do_strip_all(self, command):
        command = split_command(command)
        finalize_title_stripping(month=command[0], year=command[1])
    
    def help_strip_all(self):
        print('strip_all [month]')
        print('strips all the articles from that month')
        
    def do_delete_article(self, command):
        delete_article(article_id=command)
        
    def help_delete_article(self):
        print('delete [article_id]')
        print('deletes the selected article from the database')
        print('Note: this is currently irreversible')
        
    def do_categories(self, command):
        category_interface(command)
    
    def help_categories(self):
        print('Opens the category interface')
        print('categories add - add category')
        print('categories update - update category name')
        print('categories display - display categories')
    
    def do_finalize(self, command):
        command = split_command(command)
        finalize_article_descriptions(month=command[0], year=command[1])
    
    def help_finalize(self):
        print('finalize [month], [year]')
        print('finalize 6 2019 : finalizes the June 2019 articles')
        
    def do_export(self, command):
        export_interface(command)
        
    def help_export(self):
        print('''export [option] is used to output the article data into a finished roundup
in a docx file. [option] choices are:
export category - export roundup by category
export month - export roundup by month
export finalize - finalize title stripping
export finish_desc - finish article descriptions''')
        
#    def do_get_help(self, command):
#        '''Will probably deprecate this command later on'''
#        display_title(command)
        
    def do_display_categories(self, command):
        display_categories(command)
        
    def help_display_categories(self):
        print('Displays a list of the currently available categories.')
        
    def do_exit(self, arg):
        db.close()
        print('Exiting Roundup Generator')
        sys.exit()
        #raise SystemExit
        
    def help_exit(self):
        print('Exits the program, closes the database')
        
    def do_quit(self, arg):
        db.close()
        print("Quitting Roundup Generator")
        sys.exit()
        #raise SystemExit
        
    def help_quit(self):
        print('Exits the program, closes the database')
        
    def parse(arg):
        'Convert a series of zero or more numbers to an argument tuple'
        return tuple(map(int, arg.split()))    

    def default(self, line):       
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        try:
            exec(line) in self._locals, self._globals
        except Exception as e:
            print(e.__class__, ":", e)  
            
def main():
    #connect()
    db.connect()
    app = RGenCMD().cmdloop()
    
    
    
if __name__ == '__main__':
    main()
