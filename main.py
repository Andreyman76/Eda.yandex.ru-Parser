import asyncio
import os
import random
import threading
import time
from tkinter import *
from tkinter import messagebox
import aiohttp
import requests
from slugs import slugs

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'accept-language': 'en'}

no_picture = 'https://avatars.mds.yandex.net/get-bunker/50064/d72205e544198b757690858b7cf6245b7d8df050/orig'
DIR = os.getenv('userprofile') + '\\Downloads\\'  # Image Upload Folder


def parse_url(url: str):
    """Get data from url string"""
    url = url.replace('https://eda.yandex.ru/', '').replace('retail/', '').replace('/r/', '/')
    result = {}
    params_str = ''

    if '?' in url:
        url, params_str = url.split('?')

    region, place_slug = url.split('/')
    result['region'] = region
    result['placeSlug'] = place_slug
    params = params_str.split('&')

    if params_str:
        for i in params:
            key, value = i.split('=')
            result[key] = value

    return result


def parse_with_api(url: str) -> list[tuple]:
    """Get images from a regular service"""
    try:
        url_data = parse_url(url)
        region = url_data['region']
        region_id = slugs[region] if region in slugs.keys() else 1
        place_slug = url_data['placeSlug']
        shipping_type = f'&shippingType={url_data["shippingType"]}' if 'shippingType' in url_data.keys() else ''

        request_url = f'https://eda.yandex.ru/api/v2/menu/retrieve/{place_slug}?regionId={region_id}{shipping_type}&autoTranslate=false'
        data = requests.get(request_url, headers=headers).json()
        categories = data['payload']['categories']
        for category in categories:
            if category['name'] == 'Popular':
                categories.remove(category)
        items = [item for category in categories for item in category['items']]
        ids = []
        names = []
        images = []
        for item in items:
            item_id = item['id']
            if item_id not in ids:
                name = item['name']
                new_name = name
                i = 1
                while new_name in names:
                    new_name = name + f' ({i})'
                    i += 1
                names.append(new_name)
                picture_url = 'https://eda.yandex' + item['picture']['uri'].split('-')[
                    0] + '/orig' if 'picture' in item else no_picture
                images.append((new_name, picture_url))
                ids.append(item_id)
        return images
    except Exception as ex:
        messagebox.showerror(title='Error', message=f'An error occurred during runtime. {ex}')


def parse_retail(url: str) -> list[tuple]:
    try:
        url_data = parse_url(url)
        place_slug = url_data['placeSlug']

        response = requests.post(url='https://eda.yandex.ru/api/v2/menu/goods', headers=headers,
                                 json={'slug': place_slug, 'maxDepth': 1})

        categories = response.json()['payload']['categories']
        categories = [i['id'] for i in categories]
        items = []
        for category in categories:
            payload = {'slug': place_slug,
                       'categories': [{'id': category, 'min_items_count': 1, 'max_items_count': 1000}]}
            response = requests.post(url='https://eda.yandex.ru/api/v2/menu/goods/get-categories', headers=headers,
                                     json=payload)
            data = response.json()
            if len(data['categories']) > 0:
                items += data['categories'][0]['items']
            time.sleep(random.randint(1, 4))
        ids = []
        names = []
        images = []
        for item in items:
            item_id = item['id']
            if item_id not in ids:
                name = item['name']
                new_name = name
                i = 1
                while new_name in names:
                    new_name = name + f' ({i})'
                    i += 1
                names.append(new_name)
                if item['picture'] is None:
                    picture_url = no_picture
                else:
                    picture_url = item['picture']['url'].replace('{w}x{h}', 'orig')
                images.append((new_name, picture_url))
                ids.append(item_id)
        return images
    except Exception as ex:
        messagebox.showerror(title='Error', message=f'An error occurred during runtime. {ex}')


async def download_images(images: list[tuple], directory: str):
    """Download all images from images(name, url) to directory"""
    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for item in images:
            task = asyncio.create_task(download_image(directory, item[0], item[1], session))
            tasks.append(task)

        await asyncio.gather(*tasks)
    pass


async def download_image(directory: str, name: str, url: str, session: aiohttp.ClientSession):
    """Asynchronously loading an image by url and saving it under the name in a given directory"""
    try:
        async with session.get(url) as response:
            with open(
                    directory + name.replace('"', '\'').replace(':', '').replace('/', ' ').replace('\\', ' ') + '.jpg',
                    'wb') as file:
                data = await response.content.read()
                file.write(data)

    except Exception as ex:
        await asyncio.sleep(2)
        await download_image(directory, name, url, session)
    pass


def main():
    root = Tk()
    root.title('eda.yandex.ru parser')
    root.geometry('400x200')

    frame = Frame(root)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    url_input = Entry(frame)

    url_input.place(relx=0.1, rely=0, relwidth=0.8, relheight=0.2)

    label = Label(frame, text='The insert works only on the English keyboard layout!')
    label.place(relx=0.1, rely=0.6, relwidth=0.8, relheight=0.2)

    def start_download():
        url = url_input.get()

        if url == '':
            messagebox.showerror(title='Error', message='Passed an empty string')
        else:
            button.place_forget()
            label.configure(text="Images are being loaded. Wait...")
            label.update()
            button.update()

            images = parse_retail(url) if '/retail/' in url else parse_with_api(url)
            asyncio.run(download_images(images, DIR))
            label.configure(text="Image upload completed!")
            button.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.2)
        pass

    def button_click():
        t = threading.Thread(target=start_download)
        t.start()
        pass

    button = Button(frame, text='Download', command=button_click)
    button.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.2)

    root.mainloop()
    pass


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
