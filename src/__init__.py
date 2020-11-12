import re
import json
import requests

from typing import List, Dict
from loguru import logger
from fake_useragent import UserAgent

valid_search_type = ['documentary',
'series',
'movie',
'standUpComedySpecial',
'special',
'animeSeries',
'talk show']

class netflix:
    def __init__(self):
        self.json_url = "https://media.netflix.com/gateway/v1/en/titles/upcoming"

        self.new_struct = {}
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent.random, 'content-type': 'application/json'})

    @logger.catch
    def get_json(self):
        return self.session.get(self.json_url).json()['items']

    def get_entry(self, category:str):
        for netflix in (self.get_json()):
            nf_type = netflix['type']
            season = netflix['seasons']
            if nf_type in valid_search_type:
                if 'series' in nf_type and type(season) == int and category == "tv":
                    yield(self.struct_data(netflix))

                if 'movie' in nf_type and type(season) != int and category == "movie":
                    yield(self.struct_data(netflix))

                elif 'documentary' in nf_type and category == "documentary":
                    yield(self.struct_data(netflix))


    def get_netflix_metadata(self,nf_id:str):
        graphql_query = '{"operationName":"getOriginalHook","variables":{"country":"","locale":"en","isAuthenticated":false,"withDocuments":true,"movieId":"{NF_ID}"},"query":"query getOriginalHook($movieId: String!, $locale: String!, $country: String, $isAuthenticated: Boolean!, $withDocuments: Boolean!) {\\n original(movieId: $movieId, locale: $locale) {\\n id\\n status\\n title\\n description\\n category\\n selectedSeason\\n keyArt {\\n medium\\n __typename\\n }\\n image(size: LARGE, locale: $locale, country: $country) {\\n id\\n url\\n type\\n __typename\\n }\\n releasingInDetectedCountry\\n isOriginalInDetectedCountry\\n releasingInCoverageCountry\\n isOriginalInCoverageCountry\\n publicityContacts {\\n id\\n name\\n email\\n __typename\\n }\\n documents @include(if: $withDocuments) {\\n id\\n name\\n category\\n url\\n __typename\\n }\\n __typename\\n }\\n assetSearch(movieId: $movieId, locale: $locale, categories: []) @include(if: $isAuthenticated) {\\n totalCount\\n __typename\\n }\\n}\\n"}'.replace("{NF_ID}", nf_id)
        response = self.session.post('https://media.netflix.com/graphql',
        headers={'content-type': 'application/json'},data=graphql_query)
        return (response.json()['data'])

    def struct_data(self, data:Dict) -> Dict:
        _id = data['id']
        name = data['name']
        desc = data['description']
        locale = data['locale']
        season = data['seasons']
        uri = data['uri']

        meta = dict(dict(self.get_netflix_metadata(_id)).items())
        meta_image = meta['original']['image']['url']
        meta_desc = meta['original']['description']
        meta_desc = (re.sub(u'<[^>]*>',"",str(meta_desc)))
        meta_cat = meta['original']['category']
        meta_typename = meta['original']['__typename']
        placeholder_img = "https://loot.datapor.no/fc644b17-ab27-4917-9e11-05e800a7eb32.jpg"


        if (type(season)) == int:
            new_struct = {
            'id': _id,
            'name': name,
            'description':meta_desc,
            'category':("No Category Found" if meta_cat == None else meta_cat),
            'locale': locale,
            'seasons':season,
            'type':meta_typename,
            'img': (placeholder_img if meta_image == None else meta_image),
            'original_url': f'https://media.netflix.com{uri}'
            }
        else:
            new_struct = {
            'id': _id,
            'name': name,
            'description':meta_desc,
            'category':("No Category Found" if meta_cat == None else meta_cat),
            'locale': locale,
            'type':meta_typename,
            'img': (placeholder_img if meta_image == None else meta_image),
            'original_url': f'https://media.netflix.com{uri}'
            }

        return new_struct

    def json_pretty(self, json_struct):
        return(json.dumps(json_struct,indent=4))
