# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/20/22
"""
import logging

import coloredlogs
import requests

"""
Server must be running 
"""
if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    res = requests.post(url="http://127.0.0.1:5001/Connect/Mistayan",
                        json={'message': 'Connect'}, )
    tok = res.headers.get('token') or None
    assert res.status_code == 200

    res = requests.post(url="http://127.0.0.1:5001/Disconnect/Mistayan",
                        json={'message': 'Disconnect', 'token': tok}, )
    assert res.status_code == 200

    res = requests.post(url="http://127.0.0.1:5001/Connect/Mistayan",
                        json={'message': 'Connect', 'token': tok}, )
    assert res.status_code == 200
    tok = res.headers.get('token')

    res = requests.get(url="http://127.0.0.1:5001/Update/Mistayan",
                       json={'message': 'Update', 'token': tok})
    print(res.headers)
    print(res.content)
    print(res.raw)
    assert res.status_code == 200

    # res = requests.post(url="http://127.0.0.1:5001/Play/",
    #                     json={'player': 'Mistayan', 'message': 'Play'}
    #                     )
    # pprint.pprint(res)
    #
    # res = requests.post(url="http://127.0.0.1:5001/Give/",
    #                     json={'player': 'Mistayan', 'message': 'Give'}
    #                     )
    # pprint.pprint(res)
    #
