import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

# from threading import Thread
from datetime import datetime
from threading import Timer


keyboard = VkKeyboard(one_time=False)
keyboard.add_button('Запуск фонового поиска', color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_button('Мгновенный поиск', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Настройки поиска', color=VkKeyboardColor.POSITIVE)

keyboard1 = VkKeyboard(one_time=False)
keyboard1.add_button('Добавить слово', color=VkKeyboardColor.PRIMARY)
keyboard1.add_button('Удалить слово', color=VkKeyboardColor.POSITIVE)
keyboard1.add_line()
keyboard1.add_button('Добавить группу', color=VkKeyboardColor.PRIMARY)
keyboard1.add_button('Удалить группу', color=VkKeyboardColor.POSITIVE)

keyboard2 = VkKeyboard(one_time=False)
keyboard2.add_button('Закончить изменение набора слов', color=VkKeyboardColor.PRIMARY)
keyboard2.add_line()
keyboard2.add_button('Удалить слово', color=VkKeyboardColor.POSITIVE)
keyboard2.add_line()
keyboard2.add_button('Добавить слово', color=VkKeyboardColor.PRIMARY)
keyboard2.add_line()
keyboard2.add_button('Показать набор слов', color=VkKeyboardColor.POSITIVE)

keyboard3 = VkKeyboard(one_time=False)
keyboard3.add_button('Закончить изменение набора групп', color=VkKeyboardColor.PRIMARY)
keyboard3.add_line()
keyboard3.add_button('Удалить группу', color=VkKeyboardColor.POSITIVE)
keyboard3.add_line()
keyboard3.add_button('Добавить uhegge', color=VkKeyboardColor.PRIMARY)
keyboard3.add_line()
keyboard3.add_button('Показать набор групп', color=VkKeyboardColor.POSITIVE)


def send_message(vk_group, id, message=None, attachment=None, keyboard=None):
    vk_group.messages.send(user_id=id,
                           message=message,
                           random_id=get_random_id(),
                           attachment=attachment,
                           keyboard=keyboard.get_keyboard())

def TimerSeach(vk_group, vk_search, event, PostOwnerIdAll, PostId_lastAll, PostWordALL, TimerOn):
    now_min = datetime.now().minute
    wait = (60+1-now_min) % 30
    Timer(wait*60, Search, args = [vk_group, vk_search, event, PostOwnerIdAll, PostId_lastAll, PostWordALL, TimerOn]).start()

def Search(vk_group, vk_search, event, PostOwnerIdAll, PostId_lastAll, PostWordALL, TimerOn):
    PostLink = ''
    for PostOwnerId in PostOwnerIdAll:
        PostCount = 10
        findPost = vk_search.wall.search(owner_id=-PostOwnerId,
                                     query=PostWordALL,
                                     count=PostCount)

        PostCountCallBack = findPost.get('count')

        for i in range(min(PostCount, PostCountCallBack)):
            if (PostId := (findPost.get('items')[i]).get('id')) > PostId_lastAll[PostOwnerIdAll.index(PostOwnerId)]:
                PostLink += (f'\nhttps://vk.com/wall-{PostOwnerId}_{PostId}')
        PostId_lastAll[PostOwnerIdAll.index(PostOwnerId)] = (findPost.get('items')[0]).get('id')

    if PostLink != '':
        vk_group.messages.send(user_id=event.user_id,
                               random_id=get_random_id(),
                               message=PostLink)

    if TimerOn:
        vk_group.messages.send(user_id=event.user_id,
                               random_id=get_random_id(),
                               message=(f'Включен поиск для групп ', [f'https://vk.com/wall-{PostOwnerId}' for PostOwnerId in PostOwnerIdAll] , f' по словам {PostWordALL}'))

        TimerSeach(vk_group, vk_search, event, PostOwnerIdAll, PostId_lastAll, PostWordALL, TimerOn)

def getPostIdLast(vk_search, PostOwnerIdAll):
    PostId_last = [0]*len(PostOwnerIdAll)
    for PostOwnerId in PostOwnerIdAll:
        post = vk_search.wall.get(owner_id=-PostOwnerId,
                                  count=2)
        PostId_last[PostOwnerIdAll.index(PostOwnerId)] = (post.get('items')[1]).get('id')+1
    return PostId_last

def WordChange(vk_group, event, PostWordALL, WordAdd):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == 'Закончить изменение набора слов':
                vk_group.messages.send(user_id=event.user_id,
                                       random_id=get_random_id(),
                                       message=f'Итоговый набор слов: {PostWordALL }')
                return PostWordALL

            elif event.text == 'Удалить слово':
                WordAdd = 0
                PostWordALL = WordChange(vk_group, event, PostWordALL, WordAdd)

            elif event.text == 'Добавить слово':
                WordAdd = 1
                PostWordALL = WordChange(vk_group, event, PostWordALL, WordAdd)

            elif event.text == 'Показать набор слов':
                vk_group.messages.send(user_id=event.user_id,
                                       random_id=get_random_id(),
                                       message=f'Текущий набор слов: {PostWordALL}')

            else:
                if WordAdd:
                    PostWordALL.add(event.text)
                else:
                    try:
                        PostWordALL.remove(event.text)
                    except KeyError:
                        vk_group.messages.send(user_id=event.user_id,
                                               random_id=get_random_id(),
                                               message=f'Ошибка - в наборе нет такого слова')



def PostOwnerIdChange(vk_group, event, PostOwnerIdAll, OwnerIdAdd):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == 'Закончить изменение набора групп':
                vk_group.messages.send(user_id=event.user_id,
                                       random_id=get_random_id(),
                                       message=(f'Итоговый набор групп', [f'https://vk.com/wall-{PostOwnerId}' for PostOwnerId in PostOwnerIdAll]))
                send_message(vk_group, event.user_id, message='Настройки:', keyboard=keyboard1)
                return PostOwnerIdAll

            elif event.text == 'Удалить группу':
                OwnerIdAdd = 0
                PostOwnerIdAll = PostOwnerIdChange(vk_group, event, PostOwnerIdAll, OwnerIdAdd)

            elif event.text == 'Добавить группу':
                OwnerIdAdd = 1
                PostOwnerIdAll = PostOwnerIdChange(vk_group, event, PostOwnerIdAll, OwnerIdAdd)

            elif event.text == 'Показать набор групп':
                vk_group.messages.send(user_id=event.user_id,
                                       random_id=get_random_id(),
                                       message=(f'Текущий набор групп', [f'https://vk.com/wall-{PostOwnerId}' for PostOwnerId in PostOwnerIdAll]))

            else:
                if OwnerIdAdd:
                    PostOwnerIdAll.append(event.text)
                else:
                    try:
                        PostOwnerIdAll.remove(event.text)
                    except KeyError:
                        vk_group.messages.send(user_id=event.user_id,
                                               random_id=get_random_id(),
                                               message=f'Ошибка - в наборе нет такой группы')



def main():

    PostOwnerIdAll = []
    PostWordALL = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == 'Начать':
                send_message(vk_group, event.user_id, message = 'привет', keyboard=keyboard)
            elif event.text == 'Запуск фонового поиска':
                TimerOn = 1
                PostId_lastAll = getPostIdLast(vk_search, PostOwnerIdAll)
                Search(vk_group, vk_search, event, PostOwnerIdAll, PostId_lastAll, PostWordALL, TimerOn)

            elif event.text == 'Мгновенный поиск':
                TimerOn = 0
                Search(vk_group, vk_search, event, PostOwnerIdAll, [0]*len(PostOwnerIdAll), PostWordALL, TimerOn)

            elif event.text == 'Добавить слово':
                WordAdd = 1
                send_message(vk_group, event.user_id, message = 'Добавление слов',keyboard=keyboard2)
                PostWordALL = WordChange(vk_group, event, PostWordALL, WordAdd)

            elif event.text == 'Удалить слово':
                WordAdd = 0
                send_message(vk_group, event.user_id, message = 'Удаление слов',keyboard=keyboard2)
                PostWordALL = WordChange(vk_group, event, PostWordALL, WordAdd)

            elif event.text == 'Удалить группу':
                OwnerIdAdd = 0
                send_message(vk_group, event.user_id, message = 'Удаление групп',keyboard=keyboard3)
                PostOwnerIdAll = PostOwnerIdChange(vk_group, event, PostOwnerIdAll, OwnerIdAdd)

            elif event.text == 'Добавить группу':
                OwnerIdAdd = 1
                send_message(vk_group, event.user_id, message = 'Добавление групп',keyboard=keyboard3)
                PostOwnerIdAll = PostOwnerIdChange(vk_group, event, PostOwnerIdAll, OwnerIdAdd)

            elif event.text == 'Настройки поиска':
                send_message(vk_group, event.user_id, message = 'Настройки:',keyboard=keyboard1)



def init():
    code = '***'
    redirect_url = 'https://oauth.vk.com/blank.html'
    app = 123
    secret = '***'

    vk_session = vk_api.VkApi(app_id=app, client_secret=secret)
    try:
        vk_session.code_auth(code, redirect_url)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    print(vk_session.token['user_id'])
    print(vk_session.token['access_token'])


if __name__ =='__main__':
    # init()
    vk_session_group = vk_api.VkApi(
        token='***')  # token group
    vk_session_search = vk_api.VkApi(app_id=123,
                                     token='***',
                                     client_secret='***')
    vk_search = vk_session_search.get_api()
    vk_group = vk_session_group.get_api()
    longpoll = VkLongPoll(vk_session_group)

    main()


