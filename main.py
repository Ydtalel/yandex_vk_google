import requests
import json
import datetime
from tqdm import tqdm


class VkDownloader:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    @staticmethod
    def _find_largest_photo(dict_sizes):
        if dict_sizes["width"] >= dict_sizes["height"]:
            return dict_sizes["width"]
        else:
            return dict_sizes["height"]

    @staticmethod
    def _download_from_vk(url):
        resp = requests.get(url[0], stream=True)
        file_name = url[1] + '.jpg'
        with open("media/" + file_name, 'bw') as file:
            for part in tqdm(resp.iter_content(), desc=f"downloading photo {url[1]}.jpg from VK", unit=' kb'):
                file.write(part)

    def download_photo(self, user_acc_id, how_many_img):
        download_photo_url = self.url + 'photos.getAll'
        download_photo_params = {
            'owner_id': user_acc_id,
            'extended': True,
            'photo_sizes': True,
            'count': how_many_img,
            'need_system': True,
        }
        response = requests.get(download_photo_url, params={**self.params, **download_photo_params}).json()
        log_list = []
        check_list = []
        for photo in response['response']['items']:
            sizes = photo['sizes']
            largest = max(sizes, key=self._find_largest_photo)
            date = datetime.datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d ')
            likes = str(photo['likes']['count'])
            if likes in check_list:
                likes += f'_{date}'
            check_list.append(likes)
            log_list.append({"file_name": f"{likes}.jpg", "size": largest['type']})
            self._download_from_vk([largest['url'], likes])
            with open('log.json', 'w') as file:
                json.dump(log_list, file, indent=2, ensure_ascii=False)
        return check_list


class YandexUploader:
    url = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, file_path):
        upload_url = self.url + "resources/upload"
        headers = self.get_headers()
        params = {"path": file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def _upload(self, file_path, filename):
        href = self._get_upload_link(file_path=file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))

    def upload_to_yandex(self, list_of_photo):
        for name in tqdm(list_of_photo, desc="uploading photo to yandex", unit=' Photo', ncols=150):
            self._upload(file_path=f"VK_photos/{name}.jpg", filename=f"media/{name}.jpg")


class GoogleUploader:
    def __init__(self, token):
        self.token = token

    def upload_to_google(self, list_of_photo):
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        # folder_id = '1QKD2bIrH2V20ppRsEf_K8gk28bGgjmb4'
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        for name in tqdm(list_of_photo, desc="uploading photo to google", unit=' Photo', ncols=150):
            params = {
                "name": f"{name}",
            }

            files = {
                'data': ('metadata', json.dumps(params), 'application/json;charset=UTF-8'),
                'file': open(f"media/{name}.jpg", 'rb')
            }
            response = requests.post(url, headers=headers, files=files)


def main():
    vk = VkDownloader(vk_token, 5.131)
    data = vk.download_photo(user_id, 3)

    ya = YandexUploader(yandex_token)
    ya.upload_to_yandex(data)

    google = GoogleUploader(g_token)
    google.upload_to_google(data)
    print('data was uploaded successfully 🔥🔥🔥')


if __name__ == '__main__':
    user_id = input('Введите идентификатор пользователя вконтакте: ')
    vk_token = input('Введите ваш токен вконтакте : ')
    yandex_token = input('Введите ваш яндекс токен: ')
    g_token = input('Введите ваш google токен: ')
    main()
