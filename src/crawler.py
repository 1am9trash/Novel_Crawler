import requests as req
from bs4 import BeautifulSoup
import time
import pypandoc
import os

def connect_html(url, interval, fail_interval):
    time.sleep(interval)
    try:
        r = req.get(url)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print("connect_html() failed.")
        print("Url:", url)
        print("Error message:", e)
        return None

def get_html(url, limit=1, interval=0, fail_interval=0):
    text = None
    while text is None and limit > 0:
        limit -= 1
        text = connect_html(url, interval, fail_interval)
    return text

def query_novels(keyword):
    info = get_html("https://tw.ixdzs.com/bsearch?q=" + keyword)
    if info is None:
        print("query_novel() failed.");
        return [], [], []

    pre_url = "https://tw.ixdzs.com"
    names = []
    authors = []
    links = []

    soup = BeautifulSoup(info, "html.parser")
    novels = soup.find("div", class_="box_k").find("ul").find_all("li", recursive=False)
    for i, novel in enumerate(novels):
        links.append(pre_url + novel.find("h2", class_="b_name").find("a").attrs["href"])
        names.append(novel.find("h2", class_="b_name").text)
        authors.append(novel.find("span", class_="l1").find("a").text)

    return names, authors, links

def download_chapter(f, url):
    info = get_html(url)
    if info is None:
        print("download_chapter() failed.");
        return

    soup = BeautifulSoup(info, "html.parser")
    content = soup.find("div", class_="content").find_all("p")
    for line in content:
        f.write(line.text + "\n\n")
    f.write("\n")

def download_novel(name, author, url):
    info = get_html(url)
    if info is None:
        print("download_novel() failed.");
        return

    pre_url = "https://tw.ixdzs.com"

    f = open(name + ".md", mode="w")
    f.write("% " + name + "\n")
    f.write("% " + author + "\n\n")

    soup = BeautifulSoup(info, "html.parser")
    chapters = soup.find_all("li", class_="chapter")
    for i, chapter in enumerate(chapters):
        print("\rDownloading: {:4d}/{:4d}".format(i + 1, len(chapters)), end="")
        f.write("# " + chapter.text + "\n\n")
        download_chapter(f, pre_url + chapter.find("a").attrs["href"])
    print("\n")
    f.close()

def transform_novel(name, format):
    pypandoc.convert_file(name + ".md", format, outputfile=name + "." + format)

while True:
    keyword = input("Input keyword. Input empty string to quit.\n")
    print("")
    if keyword == "":
        break
    novel_names, novel_authors, novel_links = query_novels(keyword)
    print("Searching Keyword:", keyword)
    print("Number of Results:", len(novel_names))
    print("")
    for i in range(len(novel_names)):
        print("ID:    ", i)
        print("Name:  ", novel_names[i])
        print("Author:", novel_authors[i])
        print("")

    id = int(input("Input novel id. Input -1 to quit.\n"))
    print("")
    if id == -1:
        continue
    download_novel(novel_names[id], novel_authors[id], novel_links[id])
    transform_novel(novel_names[id], "epub")
    os.system("rm " + novel_names[id] + ".md")
