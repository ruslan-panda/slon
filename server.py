from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'Москва°': ['1521359/865c25d0b5e77750f84e', '937455/b6ad7da88856d5822e1b'],
    'Парижжжжжж': ['937455/dad7cc7bfb7440fa4550', '1652229/986a7e463d4b92868750'],
    'Нью-Йорк': ["1652229/9b0125a9092b849ea550", '1533899/cc4aba790ed3991755b9']
}

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'РџСЂРёРІРµС‚! РќР°Р·РѕРІРё СЃРІРѕС‘ РёРјСЏ!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'РќРµ СЂР°СЃСЃР»С‹С€Р°Р»Р° РёРјСЏ. РџРѕРІС‚РѕСЂРё, РїРѕР¶Р°Р»СѓР№СЃС‚Р°!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'РџСЂРёСЏС‚РЅРѕ РїРѕР·РЅР°РєРѕРјРёС‚СЊСЃСЏ, {first_name.title()}. РЇ РђР»РёСЃР°. РћС‚РіР°РґР°РµС€СЊ РіРѕСЂРѕРґ РїРѕ С„РѕС‚Рѕ?'
            res['response']['buttons'] = [
                {
                    'title': 'Р”Р°',
                    'hide': True
                },
                {
                    'title': 'РќРµС‚',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'РґР°' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = 'РўС‹ РѕС‚РіР°РґР°Р» РІСЃРµ РіРѕСЂРѕРґР°!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'РЅРµС‚' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'РќСѓ Рё Р»Р°РґРЅРѕ!'
                res['end_session'] = True
            else:
                res['response']['text'] = 'РќРµ РїРѕРЅСЏР»Р° РѕС‚РІРµС‚Р°! РўР°Рє РґР° РёР»Рё РЅРµС‚?'
                res['response']['buttons'] = [
                    {
                        'title': 'Р”Р°',
                        'hide': True
                    },
                    {
                        'title': 'РќРµС‚',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        city = random.choice(list(cities))
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        sessionStorage[user_id]['city'] = city
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Р§С‚Рѕ СЌС‚Рѕ Р·Р° РіРѕСЂРѕРґ?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = 'РўРѕРіРґР° СЃС‹РіСЂР°РµРј!'
    else:
        city = sessionStorage[user_id]['city']
        if get_city(req) == city:
            res['response']['text'] = 'РџСЂР°РІРёР»СЊРЅРѕ! РЎС‹РіСЂР°РµРј РµС‰С‘?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            return
        else:
            if attempt == 3:
                res['response']['text'] = f'Р’С‹ РїС‹С‚Р°Р»РёСЃСЊ. Р­С‚Рѕ {city.title()}. РЎС‹РіСЂР°РµРј РµС‰С‘?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'РќРµРїСЂР°РІРёР»СЊРЅРѕ. Р’РѕС‚ С‚РµР±Рµ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅРѕРµ С„РѕС‚Рѕ'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = 'Рђ РІРѕС‚ Рё РЅРµ СѓРіР°РґР°Р»!'
    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()