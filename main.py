import json
import requests
import datetime
from tqdm import tqdm


def write_response_json(data):
    with open('response.json', 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_response():
    how_many_img = 5  # максимально можем указать до 200
    params = {
        'access_token': token,
        'v': 5.131,
        'owner_id': user_id,
        'extended': True,
        'photo_sizes': True,
        'count': how_many_img,
        'need_system': True,
    }
    response = requests.get('https://api.vk.com/method/photos.getAll', params=params).json()
    write_response_json(response)


def find_largest_photo(dict_sizes):
    if dict_sizes["width"] >= dict_sizes["height"]:
        return dict_sizes["width"]
    else:
        return dict_sizes["height"]


def download_from_vk(url):
    resp = requests.get(url[0], stream=True)
    file_name = url[1] + '.jpg'
    with open("media/" + file_name, 'bw') as file:
        for part in tqdm(resp.iter_content(), desc=f"downloading photo {url[1]}.jpg from VK", unit=' kb'):
            file.write(part)


def read_response_json():
    photos = json.load(open('response.json'))['response']['items']
    log_list = []
    check_list = []
    for photo in photos:
        sizes = photo['sizes']
        largest = max(sizes, key=find_largest_photo)
        date = datetime.datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d ')
        likes = str(photo['likes']['count'])
        if likes in check_list:
            likes += f'_{date}'
        check_list.append(likes)
        log_list.append({"file_name": f"{likes}.jpg", "size": largest['type']})
        download_from_vk([largest['url'], likes])
        with open('log.json', 'w') as file:
            json.dump(log_list, file, indent=2, ensure_ascii=False)
    return check_list


def get_headers():
    return {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(yandex_token)
    }


def get_upload_link(file_path):
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = get_headers()
    params = {"path": file_path, "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=params)
    return response.json()


def upload(file_path, filename):
    href = get_upload_link(file_path=file_path).get("href", "")
    response = requests.put(href, data=open(filename, 'rb'))


def upload_to_yandex(data):
    for name in tqdm(data, desc="uploading photo to yandex", unit=' Photo', ncols=150):
        upload(file_path=f"VK_photos/{name}.jpg", filename=f"media/{name}.jpg")


def upload_to_google(data):
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    folder_id = '1QKD2bIrH2V20ppRsEf_K8gk28bGgjmb4'
    headers = {
        "Authorization": f"Bearer {g_token}"
    }
    for name in tqdm(data, desc="uploading photo to google", unit=' Photo', ncols=150):
        params = {
            "name": f"{name}",
            "parents": [folder_id]
        }

        files = {
            'data': ('metadata', json.dumps(params), 'application/json;charset=UTF-8'),
            'file': open(f"media/{name}.jpg", 'rb')
        }
        response = requests.post(url, headers=headers, files=files)


def main():
    get_response()
    data = read_response_json()
    upload_to_yandex(data)
    upload_to_google(data)
    print('data was uploaded successfully 🔥🔥🔥')


if __name__ == '__main__':
    user_id = input('Введите идентификатор пользователя Vkontakte: ')
    yandex_token = input('Введите Яндекс токен: ')
    token = input('Введите ваш токен вконтакте : ')
    g_token = input('Введите ваш токен google : ')
    main()
