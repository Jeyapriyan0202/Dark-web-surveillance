import pandas as pd
import requests
import stem.process
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import os
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
#nltk.download('punkt')
#nltk.download('stopwords')
sw = stopwords.words('english')
stemmer = PorterStemmer()

print("Before run this make u are connected to the internet otherwise this application don't work")
# Set the user agent to use for the request
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'

# Set the headers for the request
headers = {'User-Agent': user_agent}
def download(url, pathname, images ):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name
    filename = os.path.join(pathname, f'{images}.jpg')
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

def valid(url):
    parse = urlparse(url)
    if bool(parse.scheme) == True and bool(parse.netloc) == True:
        return url
    elif bool(parse.scheme) == False and bool(parse.netloc) == True:
        url = urljoin(parse_url.scheme, url)
        return url
    else:
        pass

# Set the number of links to crawl
num_links_to_crawl = 5 #int(input("Enter the number of links to crawl:"))
# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller password
    controller.authenticate(password='mypassword')
    # Set the new IP address
    controller.signal(Signal.NEWNYM)
    # Set the starting URL
    url = r"https://www.bookchor.com/"#input("enter the url you suspect:")
    url1 = url.encode('unicode-escape')
    try:
        indexofvalid  = url.index("?")
        valid_url = url[:indexofvalid]
    except:
        pass
    parse_url = urlparse(url)

    # Initialize the visited set and the link queue
    visited = set()
    site_url = [url]
    imgs_url = []
    all_data = []

    # Crawl the links
    for link in site_url:
        # Skip the link if it has already been visited
        if link in visited:
            continue

        # Set the new IP address
        controller.signal(Signal.NEWNYM)

        # Send the request to the URL
        try:
            response = requests.get(link, headers=headers).text
        except:
            continue

        # Parse the response
        soup = BeautifulSoup(response, 'html.parser')

        # Find all links on the page
        links = soup.find_all('a')
        imgs = soup.find_all("img")
        raw_data = word_tokenize(soup.text)
        text_data = []
        for word in raw_data:
            word1 = stemmer.stem(word)
            if word1 not in sw:
                text_data.append(word1)

        # collect the site links
        sites = []
        for a in links:
            url = a.get('href')
            if not url:
                # if img does not contain src attribute, just skip
                continue
            try:
                pos = url.index("?")
                url = url[:pos]
            except ValueError:
                pass
            url = valid(url)
            if url not in site_url:
                site_url.append(url)
                sites.append(url)
            else:
                sites.append(url)
                continue
        site_index = []
        for site in sites:
            site_index.append(site_url.index(site))


        # collect the images links
        image = []
        for img in imgs:
            url = img.get('src')
            if not url:
                # if img does not contain src attribute, just skip
                continue
            try:
                p = url.index("?")
                url = url[:p]
            except ValueError:
                pass
            url = valid(url)
            if url not in imgs_url:
                imgs_url.append(url)
                image.append(url)
            else:
                image.append(url)
                continue
        img_index = []
        for img in image:
            img_index.append(imgs_url.index(img))
        # Add the link to the visited set
        visited.add(link)
        data= {"link": link ,
               "text": text_data,
               "site_index": site_index,
               "image_index": img_index}
        all_data.append(data)
        if len(visited) >= num_links_to_crawl:
            break
    #print(imgs_url[85])
    for img in imgs_url:
        controller.signal(Signal.NEWNYM)
        path = r".\images"
        c = imgs_url.index(img)
        controller.signal(Signal.NEWNYM)
        try:
            download(img, path, c)
            c += 1
        except :
            continue

print("This is the url you provide to me:", link)
for url in visited:
    print("This is the crawled urls:", url)
for url in site_url:
    print("This is the site url collected from crawled sites:", url )
for url in imgs_url:
    print("This is the images url collected from crawled sites:", url)
for data in all_data:
    print("This is the collected data:", data)
df = pd.DataFrame(all_data)
df.to_csv('data.csv', index=True, header=True, mode='w' )
