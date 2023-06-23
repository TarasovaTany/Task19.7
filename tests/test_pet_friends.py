from api import PetFriends
from settings import valid_email, valid_password, not_valid_email, not_valid_password
import os

pf = PetFriends()

def test_get_api_key_for_valid_user(email = valid_email, password = valid_password):

    """ Проверяем, что запрос api ключа возвращает статус 200 и в результате содержится параметр key"""

    status, result = pf.get_api_key(email, password)

    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):

    """ Проверяем, что запрос списка всех питомцев возвращает не пустой список. Для этого сначала получаем api ключ
    и сохраняем в переменную auth_key. Далее, используя этот ключ, запрашиваем список всех питомцев и проверяем, что
    список не пустой. Доступное значение параметра filter - pf.my_pets, pf.all_pets """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0

def test_add_new_pet_with_valid_data(name='Котафей', animal_type='домашний', age='3', pet_photo='images/Cat1.jpg'):

    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_delete_self_pet():

    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Каша", "шотландский вислоухий", "2", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Паша', animal_type='шотландец', age=3):

    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

     # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
     # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_rejection_update_self_pet_info_without_name(name='', animal_type='шотландец', age=3):

    """ Проверяем невозможность очистить имя питомца путём передачи пустого поля name """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, pf.my_pets)

    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][0]['id']

    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type,  age)

    # Проверяем, что статус ответа = 200 и имя питомца не стало пустым
    assert status == 200
    assert result['name']

def test_add_pet_negative_age_number(name='Валера', animal_type='кот', age='-3', pet_photo='images/Tik.jpg'):

    '''Возможность добавления питомца с отрицательным числом в переменной age. Тест не будет пройден, если питомец будет
     добавлен на сайт с отрицательным числом в поле Возраст.'''

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_app_key(valid_email, valid_password)
    _, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)

    assert age not in result['age'], 'Питомец добавлен на сайт с отрицательным числом в поле Возраст'

def test_add_new_pet_with_empty_age(name='King', animal_type='сфинкс', age='', pet_photo_path='images/Tak.jpg'):

    """ Проверяем, что запрос на добавление нового питомца с пустым полем возраста выполняется успешно"""

    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo_path)

    assert status == 200
    assert 'name' in result

def test_add_pet_with_four_digit_age_number(name='Паша', animal_type='шотландец', age='1234', pet_photo='images/Tak.jpg'):

    '''Возможность добавления питомца с числом более трех знаков в переменной age. Тест не будет пройден, еcли питомец
    будет добавлен на сайт с числом, превышающим три знака в поле возраст.'''

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_app_key(valid_email, valid_password)
    _, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)

    number = result['age']

    assert len(number) < 4, 'Питомец добавлен на сайт с числом, прeвышающим 3 знака в поле Bозраст'

def test_rejection_update_self_pet_info_without_animal_type(name='Прося', animal_type='', age=1):

    """ Отсутствие возможности очистить типа питомца путём передачи пустого поля animal_type """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, pf.my_pets)

    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][0]['id']

    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    # Проверяем, что статус ответа = 200 и тип питомца не пустой
    assert status == 200
    assert result['animal_type']

def test_add_new_pet_with_incorrect_data_without_foto(name='%!*^@#$&', animal_type='', age=''):

    """ Проверяем, что запрос на добавление нового питомца без фото с некорректно указанными параметрами name задаётся
    спецсимволами, animal_type и age - пустые выполняется успешно."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_get_api_key_for_not_valid_email_and_password(email=not_valid_email, password=not_valid_password):

    """ Проверяем, что запрос api ключа с неверным email пользователя возвращает статус 403 и в результате не
    содержится ключа key"""

    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result

def test_add_new_pet_with_valid_data_without_foto(name='Фрося', animal_type='Котетский', age='1'):

    """ Проверяем, что запрос на добавление нового питомца без фото с указанными параметрами выполняется успешно."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_add_foto_of_pet(pet_id = '', pet_photo_path='images/Tik.jpg'):

    """Проверяем успешность запроса на добавление фото питомца по его id"""

    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, pf.my_pets)

    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][0]['id']

    status, result = pf.add_foto_of_pet(auth_key, pet_id, pet_photo_path)

    # Проверяем, что статус ответа = 200 и фото питомца соответствует заданному
    assert status == 200
    assert result['pet_photo']

def test_add_pet_with_numbers_in_variable_animal_type(name='Котэ', animal_type='34562', age='6', pet_photo='images/Tak.jpg'):

    '''Возможность добавления питомца с цифрами вместо букв в переменной animal_type.
    Тест не будет пройден, если питомец будет добавлен на сайт с цифрами вместо букв в поле порода.'''

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_app_key(valid_email, valid_password)
    status, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert animal_type not in result['animal_type'], 'Питомец добавлен на сайт с цифрами вместо букв в поле Порода'