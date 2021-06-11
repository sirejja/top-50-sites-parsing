import pandas as pd
import requests                         
from bs4 import BeautifulSoup           
import numpy as np
import sys

# Избавление от последних 'suffix' символов
def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]

# Разгруппировка полученных названий стран по тегам ul
def ungroup(grouped, names):
    names = []
    for each_group in grouped:
        for only in each_group:
            names.append(only)
    return names

# Убираем ненужные символы в введенной командной строке
def remove_char(s):
    result = s[1 : -1]
    return result


if __name__ == '__main__':
    
    # Запрос и суп html
    URL = 'https://www.alexa.com/topsites/countries'
    req = requests.get(URL) 
    soup = BeautifulSoup(req.text, 'lxml')
   
    # Избавляемся от 'countries' для перехода по новой ссылке в будущем
    URL = strip_end(URL, 'countries')

    # Создание необходимых объектов
    sites_info = list()
    country_name_grouped = list()
    country_names = list()
    parsed_urls_grouped = list()
    parsed_urls = list()
    URLs = dict()

    # Параметры, введенные из командной строки
    try:
        country_entered = sys.argv[1]
        try:
            separator = sys.argv[3]
        except:
            separator = ' '
        file_name = sys.argv[2]
    except:
        file_name = None

    # Поиск нужной ссылки для введенной страны
    for URLs_row in soup.find_all('ul', attrs={'class': 'countries span3'}):
        country_name_grouped.append([element.text.replace('\n', '') for element in URLs_row.find_all('a')])
        parsed_urls_grouped.append([element.get('href') for element in URLs_row.find_all('a')]) 

    # Разгруппировка полученных названий стран по тегам ul
    parsed_urls = ungroup(parsed_urls_grouped, parsed_urls)
    country_names = ungroup(country_name_grouped, country_names)
    
    # заполнение словаря ссылок
    for (element_country, element_url) in zip(country_names, parsed_urls):
            URLs[element_country] = element_url

    # На всякий случай предостережемся от ошибок
    try:
        URL += URLs[country_entered]
        req = requests.get(URL)
        soup = BeautifulSoup(req.text, 'lxml')

        # Считываем данные таблицы построчно
        for table_row in soup.find_all('div', attrs={'class': 'tr site-listing'}):
            sites_info.append([element.text.replace('\n', '') for element in table_row.find_all('div')])

        # Название колонок
        heading_table = ['Rank', 'Site', 'Daily Time on Site', 'Daily Pageviews per Visitor', '% of Traffic From Search', 'Total Sites Linking In']
        sites_info = pd.DataFrame(sites_info, columns = heading_table, index=np.arange(1, len(sites_info)+1)) 
        
        # Проверка на заполненность аргументов из командной строки
        if  file_name != None:
            # Запаска на случай сложных разделителей, состоящих из более чем одного символа(плохая обработка исключений на скорую руку)
            try:
                sites_info.to_csv(f"{file_name}.csv", index=None, sep=f'{separator}')                   # для однозначного разделителя
            except:
                np.savetxt(f'{file_name}.csv', sites_info, delimiter=f'{separator}',fmt='%s')           # для неоднозначного разделителя по типу \t   
        else:
            print(sites_info)
    except:
        print('No such country or troubles with site.\nMaybe you forgot to type the country?')