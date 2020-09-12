import datetime as dt
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


class APIConnect:
    """ Класс для получения информации через API
    """
    LOGIN = os.getenv('login')
    APIKEY = os.getenv('apikey')

    def __init__(self):
        """ Конструктор класса
            При создании экземпляра получают хост API. И переменные
            для авторизации, которые сохраняет в словаре.
        """
        self.host = os.getenv('host')
        self.api_host = os.getenv('api_host')
        self.headers = {
            "login": self.LOGIN,
            "APIKEY": self.APIKEY
        }

    def get_catalogs(self):
        """ Метод для получения списка и основных параметров каталогов.
        :return: Матрица со списком каталогов и доп. параметров.
        """
        genders = ('mens', 'womens')
        api_slug = '/catalog/sections/get/'

        catalogs = []

        for gender in genders:
            payload = {
                "gender_code": gender
            }

            catalog = requests.post(
                f'{self.api_host}{api_slug}',
                json=payload,
                headers=self.headers
            )

            catalog_dict = catalog.json()['data']

            for item in catalog_dict:
                catalog_id = item['id']
                catalog_parent_id = item['parent_iblock_id']
                catalog_name = item['name']
                catalog_url = self.host + item['section_page_url']
                updated = dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                answer = [
                    gender, catalog_id, catalog_parent_id,
                    catalog_name, catalog_url, updated
                ]

                catalogs.append(answer)

        print('Собрали все каталоги')

        return catalogs

    def count_items(self):
        """ Подсчет количества товаров в каталогах
        :return: Матрица со списком каталогов, параметров и количества
                 товаров.
        """
        catalogs = self.get_catalogs()
        api_slug = '/catalog/products/getBySectionId/'

        for catalog in catalogs:
            items_counter = 0

            for page in range(1, 50):

                gender_dict = {
                    'mens': 36360,
                    'womens': 36361
                }

                gender_code = gender_dict[catalog[0]]

                payload = {
                    "page": page,
                    'gender': gender_code
                }

                items = requests.post(
                    f'{self.api_host}{api_slug}{catalog[1]}/',
                    json=payload,
                    headers=self.headers
                )

                try:
                    if items.json()['data']:
                        items_counter += len(items.json()['data'])
                except KeyError:
                    break
            catalog.append(items_counter)

            print('Подсчитали колличество товаров в разделе')

        print('Подсчитали колличество товаров во всех разделах')

        return catalogs

    def export_to_scv(self):
        """ Экспорт данных в xlsx
        :return: xlsx файл.
        """
        column_names = [
            'gender', 'id', 'parrent_id', 'name', 'url',
            'updated', 'items_count'
        ]
        column_values = self.count_items()

        df = pd.DataFrame(data=column_values, columns=column_names)

        create_time = dt.datetime.now().strftime("%d-%m-%Y")
        df.to_excel(
            f'catalog_{create_time}.xlsx', index=False
        )


def main():
    connect = APIConnect()
    connect.export_to_scv()


if __name__ == "__main__":
    main()
