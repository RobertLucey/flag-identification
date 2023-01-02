import os
from multiprocessing.pool import ThreadPool

import bs4
import requests
from PIL import Image
import aspose.words as aw

from flag_identification.settings import RAW_DIR
from flag_identification.utils import is_text_flaggy


HEADERS = {
    "User-Agent": "CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)"
}


def process(url):
    cat = url.split("/")[-1]
    category_modified = cat.replace("_", "-")

    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text)

    body = soup.find("div", {"id": "bodyContent"})
    imgs = body.find_all("img")

    for img in imgs:
        if img.parent.get("href"):
            if is_text_flaggy(img.parent.get("href")):
                url = "https://commons.wikimedia.org" + img.parent.get("href")

                if url.endswith("svg"):
                    response = requests.get(url)
                    soup = bs4.BeautifulSoup(response.text)
                    link = soup.find("div", {"id": "file", "class": "fullImageLink"})
                    imgs = link.find_all("img")

                    if len(imgs) > 1:
                        print("too many images")

                    name = imgs[0].get("alt").replace("File:", "")
                    url = imgs[0].get("src")

                    tmp_path = f"/tmp/{name}"
                    file_path = os.path.join(
                        RAW_DIR,
                        f'{category_modified}_{name.replace(".svg", ".png").replace(".SVG", ".png")}',
                    )

                    if os.path.exists(file_path):
                        continue

                    img_data = requests.get(url, headers=HEADERS).content
                    with open(tmp_path, "wb") as handler:
                        handler.write(img_data)

                    doc = aw.Document()
                    builder = aw.DocumentBuilder(doc)

                    try:
                        shape = builder.insert_image(f"/tmp/{name}")
                    except:
                        print(f"Bad svg: {url}")
                        continue

                    page_setup = builder.page_setup
                    page_setup.page_width = shape.width
                    page_setup.page_height = shape.height
                    page_setup.top_margin = 0
                    page_setup.left_margin = 0
                    page_setup.bottom_margin = 0
                    page_setup.right_margin = 0

                    # save as PNG
                    try:
                        doc.save(file_path)
                    except:
                        print(f"Failed to save svg as png: {url}")

                elif url.endswith("jpg") or url.endswith("JPG"):
                    response = requests.get(url)
                    soup = bs4.BeautifulSoup(response.text)
                    link = soup.find("div", {"id": "file", "class": "fullImageLink"})
                    imgs = link.find_all("img")

                    if len(imgs) > 1:
                        print(f"too many images: {url}")

                    name = imgs[0].get("alt").replace("File:", "")
                    url = imgs[0].get("src")

                    tmp_path = f"/tmp/{name}"
                    file_path = os.path.join(
                        RAW_DIR,
                        f'{category_modified}_{name.replace(".JPG", ".png").replace(".jpg", ".png")}',
                    )

                    if os.path.exists(file_path):
                        continue

                    img_data = requests.get(url, headers=HEADERS).content
                    with open(tmp_path, "wb") as handler:
                        handler.write(img_data)

                    try:
                        im = Image.open(f"/tmp/{name}")
                    except:
                        print(f"Could not open image: /tmp/{name}    {url}")

                    try:
                        im.save(file_path)
                    except:
                        print(f"Cannot save as png: /tmp/{name}    {url}")

                elif url.endswith("png") or url.endswith("PNG"):

                    response = requests.get(url)
                    soup = bs4.BeautifulSoup(response.text)
                    link = soup.find("div", {"id": "file", "class": "fullImageLink"})
                    imgs = link.find_all("img")

                    if len(imgs) > 1:
                        print("too many images")

                    name = imgs[0].get("alt").replace("File:", "")
                    url = imgs[0].get("src")

                    file_path = os.path.join(
                        RAW_DIR, category_modified + "_" + name.replace(".PNG", ".png")
                    )

                    if os.path.exists(file_path):
                        continue

                    img_data = requests.get(url, headers=HEADERS).content
                    try:
                        with open(file_path, "wb") as handler:
                            handler.write(img_data)
                    except:
                        print(f"Can't write to file: {file_path}    {url}")

                elif url.endswith("gif") or url.endswith("gif"):
                    print("gif")

                elif url.endswith("jpeg") or url.endswith("JPEG"):
                    print("jpeg")

                else:
                    print(f"not sure what to do with {url}")

            else:
                # FIXME: Can worry about these later
                print(f'NOT FLAGGY ENOUGH NAME: {img.parent.get("href")}')


def main():
    home_url = "https://commons.wikimedia.org/wiki/Category:Gallery_pages_about_flags"
    response = requests.get(home_url)
    soup = bs4.BeautifulSoup(response.text)

    body = soup.find("div", {"class": "mw-content-ltr"})

    urls = []
    for li in body.find_all("li"):
        href = li.find("a").get("href")
        urls.append("https://commons.wikimedia.org" + href)

    with ThreadPool(processes=10) as pool:
        pool.map(process, urls)


if __name__ == "__main__":
    main()
