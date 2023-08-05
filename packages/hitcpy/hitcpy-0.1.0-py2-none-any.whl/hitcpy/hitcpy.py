import requests
import json


def put(url, params=None):
    return requests.put(url, data=params)

    
def get(url, params=None):
    return requests.get(url, params=params)


def post(url, params=None):
    return requests.post(url, data=params)


def delete(url):
    return requests.delete(url)


class HITC(object):
    def __init__(self, url):
        self.url = url+'/'
        # make sure we have tried to connect to a valid api
        r = requests.get(self.url)
        if r.text.strip() != "Rest API":
            raise ValueError("Not a valid HITC API")

    def create_model(self, model_params=None):
        r = post(self.url+'models', json.dumps(model_params))
        return Model(r.json(), self.url)

    def get_model(self, guid):
        request = get(self.url + 'models/'+guid)
        if request.status_code != 200:
            return None
        return Model(request.json(), self.url)

    def get_all_models(self):
        return [Model(m, self.url) for m in get(self.url+'models').json()]

    
class Model(object):
    def __init__(self, req, url):
        # make a model from json
        self.guid = req['guid']
        self.params = req['params']
        if 'info' in req:
            self.info = req['info']
        self.predicted_field = req['predicted_field']
        self.seen = 0
        self.temporal_field = req['tfield']
        self.last = None
        self.deleted = False
        self.url = url
        
    def reset(self):
        return get(self.url+'models/reset/'+self.guid)

    def delete(self):
        self.deleted = True
        return delete(self.url+'models/'+self.guid)

    def run(self, row):
        r = put(self.url+'models/'+self.guid, json.dumps(row))
        if r.status_code != 200:
            raise ValueError(r.reason)
            return None
        else:
            r = r.json()
            self.seen = r[len(r) - 1]['predictionNumber']
            self.last = r[len(r) - 1]['rawInput']
            return r

