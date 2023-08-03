#!/usr/bin/env python
# coding: utf-8

import requests
import json


def test_service():
    url = 'http://0.0.0.0:8080/predict'
    feature_cols = ['horsepower','places', 'doors','speed', 'consumption', 'acceleration']
    
    myobj = {'horsepower':[100, 50],'places':[5, 5], 'doors':[5, 5],'speed':[190, 150], 'consumption':[10, 12], 'acceleration':[12, 18] }
    
    x = requests.post(url, json = myobj)
    
    print(x.text)

    try:
        print(json.loads(x.text))
        assert True
    except:
        assert False

if __name__ == "__main__":
    test_service()




