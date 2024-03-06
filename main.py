import os

from bs4 import BeautifulSoup
import requests
from duckduckgo_search import DDGS


def fix_slash_sharp(s):
    ret = ''.join(c if c != '/' else '_' for c in s)
    return ret if ret != 'C#' else 'C sharp'


def write_page_front_matter(name, f, title):
    f.write(f'---\ntitle: {title}\npermalink: /lab1/{fix_slash_sharp(name).lower()}/\nlayout: page\n---\n')


def write_files(desc, top20_list, info):
    with open('list.md', 'w', encoding='utf-8') as l:
        write_page_front_matter('List', l, '\'The most popular programming languages:\'')
        for i, (name, rating, _) in enumerate(top20_list):
            l.write(f'{i + 1}. [{name}](../{fix_slash_sharp(name).lower()})'
                    f' - ratings: {rating}\n'
                    f'![alt text](/awww-exercises/images/{fix_slash_sharp(name)}_img.png) \n\n')
            with open(f'{(fix_slash_sharp(name).lower())}.md', 'w', encoding='utf-8') as f:
                write_page_front_matter(name, f, name)
                f.write('\n' + desc[i]['text'])
                f.write(f'\n\n---\n\n [source]({desc[i]["url"]})')
    with open('lab1.md', 'w', encoding='utf-8') as m:
        write_page_front_matter('',m, '\'Programming language:\'')
        m.write('\n' + info['text'])
        m.write('\n\n[List of the most popular programming languages](/awww-exercises/lab1/list)')
        m.write(f'\n\n---\n\n [source]({info["url"]})')


def scrape(s: BeautifulSoup, site_addr) -> list:
    top20_list = s.find('table', {'id': "top20"}).find('tbody').find_all('tr')
    top20_list = [x.find_all('td') for x in top20_list]

    # Get the list
    top20_list = [[x[4].contents[0],
                   x[5].contents[0],
                   site_addr + x[3].findChild()['src']]
                  for x in top20_list]
    return top20_list


def get_images(top20_list):
    c = os.getcwd()
    if not os.path.isdir(c + '/images'):
        os.mkdir(c + '/images')
    # Get images and write them to files
    for name, _, img_link in top20_list:
        r = requests.get(img_link, stream=True)
        r.raise_for_status()

        file_name = fix_slash_sharp(name)
        if not os.path.exists(c + '/images/' + file_name + '_img.png'):
            with open(c + '/images/' + file_name + '_img.png', 'wb') as f:
                f.write(r.content)


def get_descriptions(top20_list: list) -> list:
    info = []
    for name, _, _ in top20_list:

        # Fix the names for specific languages so DuckDuckGo can get the answers
        fixed_name = name

        if name == 'C#':
            fixed_name = 'C sharp'
        elif name == 'Delphi/Object Pascal':
            fixed_name = name.split('/')[0]

        if not fixed_name.endswith('language'):
            fixed_name = fixed_name + ' programming language'

        answer = DDGS().answers(fixed_name)
        try:
            info.append(next(answer))
        except StopIteration:
            print(name + ' failed')
    return info


def get_pl_info():
    answer = DDGS().answers('Programming language')
    return next(answer)


if __name__ == '__main__':
    docs_path = '/docs'
    cwd = os.getcwd()
    os.chdir(cwd + docs_path)

    site = 'https://www.tiobe.com/'
    page_addr = 'https://www.tiobe.com/tiobe-index/'
    response = requests.get(page_addr)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    top20 = scrape(soup, site)
    # get_images(top20)
    descriptions = get_descriptions(top20)
    pl_info = get_pl_info()
    write_files(descriptions, top20, pl_info)
