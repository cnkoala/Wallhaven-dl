########################################################
#        Program to Download Wallpapers from           #
#                  alpha.wallhaven.cc                  #
#                                                      #
#                 Author - Saurabh Bhan                #
#                                                      #
#                  dated- 26 June 2016                 #
#                 Update - 29 June 2016                #
#               update - 11 Oct 2017 by cnkoala        #
########################################################

import os
import getpass
import bs4
import re
import requests
from tqdm import tqdm
import urllib 

os.makedirs('Wallhaven', exist_ok=True)

def inputnum(maxnum,defaultoption,text):
    while True:
        n = input(text)
        if n == '':
            print ('The default option: %d is chosen'% defaultoption)
            n = str(defaultoption)
            return n
            break
        elif not str.isdigit(n):
            print('%s is not a number.Please input a number\n' %n )
        elif int(n) <=0:
            print('%s is below or same as zero. Please input a number which is bigger than zero\n' %n)
        elif int(n) > maxnum:
            print('There is no choice has been found. Please input the correct number')
        else:
            return n
            break
        
def login():
    print('NSFW images require login')
    username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    req = requests.post('https://alpha.wallhaven.cc/auth/login', data={'username':username, 'password':password})
    return req.cookies

def category():
    print('''****************************************************************
                            Category Codes
    1:all     - Every wallpaper.
    2:general - For 'general' wallpapers only.
    3:anime   - For 'Anime' Wallpapers only.
    4:people  - For 'people' wallapapers only.(d)
    5:ga      - For 'General' and 'Anime' wallapapers only.
    6:gp      - For 'General' and 'People' wallpapers only.
    ****************************************************************
    ''')
    ccode = inputnum(6,4,'Enter Category: ')
    ALL = '111'
    ANIME = '010'
    GENERAL = '100'
    PEOPLE = '001'
    GENERAL_ANIME = '110'
    GENERAL_PEOPLE = '101'
    if ccode == "1":
        ctag = ALL
    elif ccode == "2":
        ctag = ANIME
    elif ccode == "3":
        ctag = GENERAL
    elif ccode == "4":
        ctag = PEOPLE
    elif ccode == "5":
        ctag = GENERAL_ANIME
    elif ccode == "6":
        ctag = GENERAL_PEOPLE

    print('''
    ****************************************************************
                            Purity Codes
    1:sfw     - For 'Safe For Work'
    2:sketchy - For 'Sketchy'
    3:nsfw    - For 'Not Safe For Work'(d)
    4:ws      - For 'SFW' and 'Sketchy'
    5:wn      - For 'SFW' and 'NSFW'
    6:sn      - For 'Sketchy' and 'NSFW'
    7:all     - For 'SFW', 'Sketchy' and 'NSFW'
    ****************************************************************
    ''')
    pcode = inputnum(7,3,'Enter Purity: ')
    ptags = {'1':'100', '2':'010', '3':'001', '4':'110', '5':'101', '6':'011', '7':'111'}
    ptag = ptags[pcode]

    if pcode in ['3', '5', '6', '7']:
        cookies = login()
    else:
        cookies = dict()
    CATURL = 'https://alpha.wallhaven.cc/search?categories=' + \
        ctag + '&purity=' + ptag

    return (CATURL, cookies)
    

def latest():
    print('Downloading latest')
    latesturl = 'https://alpha.wallhaven.cc/latest?'
    return (latesturl, dict())

def search():
    query = input('Enter search query: ')
    searchurl = 'https://alpha.wallhaven.cc/search?q=' + \
        urllib.parse.quote_plus(query) 
    return (searchurl, dict())

def advs():
    CATURL, cookies = category()

    query = input('Enter search query(Enter directly for skip): ').lower()
    if not query == '':
        CATURL  = CATURL + '&q=' + urllib.parse.quote_plus(query)
        
    sorting = inputnum(5,3,'''Choose how you want to sorting the images:
1:relevance
2:favorites
3:views(d)
4:date added
5:toplist
Enter the number:''')
    stype = ['','relevance','favorites','views','date_added','toplist']
    CATURL = CATURL + '&sorting=' + stype[int(sorting)]
    
    CATURL = CATURL + '&order=desc'
    
    
    return (CATURL, cookies)

def main():
        

Choice = inputnum(4,4,'''Choose how you want to download the image:

Enter 1 for category: downloading wallpapers from specified categories
Enter 2 for latest: downloading latest wallpapers
Enter 3 for search: for downloading wallpapers from search
Enter 4 for advanced search: with more para search(d)

Enter choice: ''')


if Choice == '1':
    BASEURL, cookies = category()
elif Choice == '2':
    BASEURL, cookies = latest()
elif Choice == '3':
    BASEURL, cookies = search()
elif Choice == '4':
    BASEURL, cookies = advs()    

BASEURL = BASEURL + '&page='

pgid = int(input('How Many pages you want to Download: '))
print('Number of Wallpapers to Download: ' + str(24 * pgid))
for j in range(1, pgid + 1):
    totalImage = str(24 * pgid)
    url = BASEURL + str(j)
    urlreq = requests.get(url, cookies=cookies)
    soup = bs4.BeautifulSoup(urlreq.text, 'lxml')
    soupid = soup.findAll('a', {'class': 'preview'})
    res = re.compile(r'\d+')
    imgid = res.findall(str(soupid))
    imgext = ['jpg', 'png', 'bmp']
    for i in range(len(imgid)):
        currentImage = (((j - 1) * 24) + (i + 1))
        surl = 'http://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-%s.' % imgid[
            i]
        for ext in imgext:
            iurl = surl + ext
            osPath = os.path.join('Wallhaven', os.path.basename(iurl))
            if not os.path.exists(osPath):
                imgreq = requests.get(iurl, cookies=cookies,stream=True)
                if imgreq.status_code == 200:
                    print("Downloading : %s - %s / %s" % ((os.path.basename(iurl)), currentImage , totalImage))
                    with open(osPath, 'ab') as imageFile:
                        for chunk in tqdm(imgreq.iter_content(),total=int(imgreq.headers['content-length'])):
                            imageFile.write(chunk)
                    break
            else:
                print("%s already exist - %s / %s" % (os.path.basename(iurl), currentImage , totalImage))

if __name__ == '__main__':
    main()
