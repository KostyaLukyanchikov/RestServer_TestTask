import re
import main_methods
import markdown
from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
from api_helpers import get_paginated_list, filter_not_found

"""Initializing flask app"""
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False
api = Api(app)


# Index Page rendering from readme
class IndexPage(Resource):
    @staticmethod
    def get():
        with open("readme.md", "r", encoding="utf-8") as input_file:
            text = input_file.read()
        extensions = ['toc', 'smarty', 'fenced_code']
        html = markdown.markdown(text, extensions=extensions, output_format='html5')
        return make_response(html)


# Class that provides access to the get_city_info method
class GetCity(Resource):
    @staticmethod
    def get(city_id):
        if not re.match(r'^\d+$', city_id):
            return make_response(jsonify({'error': 'Please enter a set of digits'}), 404)
        city_info = main_methods.get_city_info(int(city_id))
        if city_info:
            return jsonify(city_info)
        else:
            return make_response(jsonify({'error': 'No city found with such geonameid'}), 404)


# Class that provides access to the get_cities_info method
class GetCities(Resource):
    @staticmethod
    def get(list_of_cities):
        if not re.match(r'^(([Ёёа-яА-Яa-zA-z-`\'\s]+)((,\s[Ёёа-яА-Яa-zA-z-`\'\s]+)|(,[Ёёа-яА-Яa-zA-z-`\'\s]+))*)$',
                        list_of_cities):
            return make_response(
                jsonify({'error': 'Please input a list of cities names, separated by \',\' or \', \''}),
                404)
        cities_info = main_methods.get_cities_info(list_of_cities)
        # none_value is always none for get_cities_info, cause filter_not_found() returns comparison as third value
        cities_not_found, cities_found, none_value = filter_not_found(cities_info)
        if cities_found is None:
            return make_response(jsonify(cities_not_found))
        cities_found = get_paginated_list(
            cities_found["Cities"],
            url='/cities/' + list_of_cities,
            start=request.args.get('start', 1),
            limit=request.args.get('limit', 5))
        if cities_not_found is None:
            return make_response(jsonify(cities_found))
        else:
            return make_response(jsonify(cities_not_found, cities_found))


# Class that provides access to the compare_cities method
class GetCitiesComparison(Resource):
    @staticmethod
    def get(two_cities_list):
        if not re.match(r'^(([Ёёа-яА-Я-`\'\s]+)((,\s[Ёёа-яА-Я-`\'\s]+)|(,[Ёёа-яА-Я-`\'\s]+)))$', two_cities_list):
            return make_response(
                jsonify({'error': 'Please input two cities names in russian, separated by \',\' or \', \''}),
                404)
        cities_comparison_info = main_methods.compare_cities(two_cities_list)
        cities_not_found, cities_found, cities_comparison = filter_not_found(cities_comparison_info)
        if cities_found is None:
            return make_response(jsonify(cities_not_found))
        if cities_not_found is None:
            return make_response(jsonify(cities_found, cities_comparison))
        else:
            return make_response(jsonify(cities_not_found, cities_found))


api.add_resource(IndexPage, '/')
api.add_resource(GetCity, '/city/<string:city_id>')
api.add_resource(GetCities, '/cities/<string:list_of_cities>')
api.add_resource(GetCitiesComparison, '/compare_cities/<two_cities_list>')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
