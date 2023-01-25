import json
import requests
import yadisk
import datetime
from tqdm import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

how_many_img = 5  # максимально можем указать до 200


def write_response_json(data):
    with open('response.json', 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_response():
    # please, do not copy my token
    token = 'vk1.a.T1U4QLxClpB8zSkQfVMGEqSiRAAx6qFo8cnnXBwMvYeEPaNT9cnHHEx_rVBDsIjOYaIoKyIKaN3QAr' \
            '6s7Koep1cjmkLjYb_9JRaWLfOKYfeZDeTIxQmCE_mL0tuKgMZa-XuJQ2Y2em3um7uFcfhyYPLHeVNYOuTHHczsKdoF_' \
            'eL7WF4sQkt2xKBwmg2V_buGL4cz8GcA6lo7gmRUAU9JMw'
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


def upload_to_yandex(data):
    disk = yadisk.YaDisk(token=yandex_token)
    disk.mkdir('/VK_photos')
    for name in tqdm(data, desc="uploading photo to yandex", unit=' Photo', ncols=150):
        disk.upload(f"media/{name}.jpg", f"/VK_photos/{name}.jpg")


def upload_to_google(directory=''):
    google_auth = GoogleAuth()
    google_auth.LocalWebserverAuth()
    drive = GoogleDrive(google_auth)
    for file_name in tqdm(os.listdir(directory), desc="uploading photo to google", unit=' Photo', ncols=150):
        photo = drive.CreateFile({'title': f'{file_name}'})
        photo.SetContentFile(os.path.join(directory, file_name))
        photo.Upload()


def main():
    get_response()
    data = read_response_json()
    upload_to_yandex(data)
    upload_to_google(directory='media/')
    print('data was uploaded successfully 🔥🔥🔥')


if __name__ == '__main__':
    user_id = input('Введите идентификатор пользователя Vkontakte: ')
    yandex_token = input('Введите Яндекс токен: ')
    main()
