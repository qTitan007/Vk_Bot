import random
import threading
import time
from pathlib import Path

import pandas as pd
import vk_api
from flask import Flask, render_template
from vk_api.bot_longpoll import VkBotLongPoll

import quote_api
from data import db_session
from data.config import Config
from data.imagery import Imagery
from data.images import Images
from data.quote import Quote

config = Config()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/data_list.db")
imagery_id = 1
app.register_blueprint(quote_api.blueprint)


class New_day():
    def __init__(self):
        self.session = db_session.create_session()
        self.flag = False
        self.config = Config()
        db_session.global_init("db/data_list.db")

    def new_day(self):
        global imagery_id
        vk_session = vk_api.VkApi(token=self.config.token)
        vk = vk_session.get_api()
        imagery_id = random.randint(1, len(self.session.query(Imagery).all()))
        if not self.flag:
            self.flag = True
            message = self.session.get(Quote, random.randint(1, len(self.session.query(Quote).all())))
            vk.wall.post(owner_id=int(f'-{self.config.club_id}'), from_group=1, message=message.value)
        elif self.flag:
            self.flag = False
            images = self.session.get(Images, random.randint(1, len(self.session.query(Images).all())))
            vk_photo_id = 'photo{}_{}.'.format(images.owner_id, images.photo_id)
            vk.wall.post(owner_id=int(f'-{self.config.club_id}'), from_group=1, attachments=[vk_photo_id])

    def run(self):
        while True:
            self.new_day()
            time.sleep(60 * 60)


def chat():
    db_session.global_init("db/data_list.db")
    vk_session = vk_api.VkApi(token=config.key)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, config.club_id)
    session = db_session.create_session()
    flag = False
    for event in longpoll.listen():
        if event.obj.message:
            if not flag:
                vk.messages.send(
                    peer_id=event.obj.message['from_id'],
                    message='Команды: персональный мем, персональная цитата, какой я джейсон сегодня',
                    random_id=random.randint(0, 2 ** 64))
                flag = True
            elif flag:
                text = event.obj.message['text']
                if text:
                    if text == 'персональный мем':

                        images = session.get(Images, random.randint(1, len(session.query(Images).all())))
                        vk_photo_id = 'photo{}_{}'.format(images.owner_id, images.photo_id)

                        vk.messages.send(peer_id=event.obj.message['from_id'],
                                         attachment=vk_photo_id,
                                         random_id=random.randint(0, 2 ** 64))

                    elif text == 'персональная цитата':
                        message = session.get(Quote, random.randint(1, len(session.query(Quote).all())))
                        vk.messages.send(peer_id=event.obj.message['from_id'], message=message.value,
                                         random_id=random.randint(0, 2 ** 64))
                    elif text == 'какой я джейсон сегодня':
                        imagery = session.get(Imagery, imagery_id)
                        imagery_photo = 'photo{}_{}.'.format(imagery.owner_id, imagery.photo_id)
                        vk.messages.send(peer_id=event.obj.message['from_id'],
                                         message=f'Сегодня ты - {imagery.description} Джейсон',
                                         attachment=imagery_photo,
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(peer_id=event.obj.message['from_id'],
                                         message='Некорректная команда',
                                         random_id=random.randint(0, 2 ** 64))


def main():
    if input('Первый запуск?  (да/нет): ') == 'да':
        print('Загрузка...')
        db_upload()
        upload_photo()

    threading.Thread(target=New_day().run, args=()).start()
    threading.Thread(target=chat, args=()).start()
    threading.Thread(target=app.run, args=()).start()


def upload_photo():
    vk_session = vk_api.VkApi(token=config.token)
    session = db_session.create_session()
    upload = vk_api.VkUpload(vk_session)

    photos = ([i.link for i in session.query(Images).all()])
    for i in range(len(photos)):
        photo = upload.photo(
            photos[i],
            album_id=config.album_memes,
            group_id=config.club_id
        )
        images = session.query(Images).filter(Images.id == (i + 1)).first()
        images.owner_id = photo[0]['owner_id']
        images.photo_id = photo[0]['id']
        session.commit()

    photos = ([i.link for i in session.query(Imagery).all()])
    for i in range(len(photos)):
        photo = upload.photo(
            photos[i],
            album_id=config.album_imagery,
            group_id=config.club_id
        )
        imagery = session.query(Imagery).filter(Imagery.id == (i + 1)).first()
        imagery.owner_id = photo[0]['owner_id']
        imagery.photo_id = photo[0]['id']
        session.commit()


def db_upload():
    session = db_session.create_session()

    calls_df, = pd.read_html("https://sevimi.by/new/top-100-czitat-dzhejsona-stethema-realnyh-i-vymyshlennyh/")
    for i in calls_df[0]:
        quote = Quote(value=i)
        session.add(quote)
        session.commit()

    for i in range(sum(1 for x in Path('static/img/memes/').iterdir())):
        images = Images(link=f'static/img/memes/{i + 1}.jpg')
        session.add(images)
        session.commit()

    description_list = {'1': 'осторожный',
                        '2': 'расчётливый',
                        '3': 'вдохновлённый',
                        '4': 'агрессивный',
                        '5': 'романтичный',
                        '6': 'ностальгирующий',
                        '7': 'наблюдательный',
                        '8': 'слабоумный и отчаянный',
                        '9': 'недовольный погодой',
                        '10': 'поэтичный'}
    for i in description_list:
        imagery = Imagery(link=f'static/img/imagery/{i}.jpg', description=f'{description_list[i]}')
        session.add(imagery)
        session.commit()


@app.route('/vk_stat/<int:group_id>')
def vk_stat(group_id):
    try:
        vk_session = vk_api.VkApi(token=config.token)
        vk = vk_session.get_api()
    except Exception:
        return 'Недействительный токен'
    try:
        response = vk.stats.get(group_id=group_id)
    except Exception:
        return 'Некорректно введена id группы'

    activities = {}
    for i in response[0]['activity']:
        activities[i] = response[0]['activity'][i]

    ages = {}
    for i in response[0]['reach']['age']:
        ages[i['value']] = i['count']

    cities = []
    for i in response[0]['reach']['cities']:
        cities.append(i['name'])

    data = {'Activities': activities, 'Ages': ages, 'Cities': cities}
    return render_template('index.html', title='Vk.Statistics', data=data)


if __name__ == '__main__':
    main()
