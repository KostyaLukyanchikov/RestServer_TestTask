import pandas as pd
import datetime
import pytz
import difflib

columns = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude",
           "feature class", "feature code", "country code", "cc2", "admin1 code", "admin2 code",
           "admin3 code", "admin4 code", "population", "elevation", "dem", "timezone", "modification date"]

table = pd.read_csv('resources/RU.txt', header=None, sep="\t", low_memory=False, names=columns, encoding="utf-8")

new_table = table.copy()
new_table = new_table.loc[table['feature class'] == 'P']

new_table['allnames'] = new_table['name'].astype(str) + ", " + new_table['asciiname'].astype(str) \
                        + ", " + new_table['alternatenames'].astype(str)

new_table['allnames'] = new_table['allnames'].str.replace(', nan', '').astype(str) \
    .apply(lambda x: list(set(map(str.strip, x.lower().split(',')))))

uniq_words = list(set([word for row in new_table['allnames'] for word in row]))


def get_city_info(geonameid):
    result = table.loc[table['geonameid'] == geonameid].astype('str').to_dict(orient='records')
    return result


def get_cities_info(url_cities):
    cities = url_cities_to_list_of_cities(url_cities)
    df_of_cities, not_found_cities = check_df_for_cities(cities, False)
    df_of_cities = df_of_cities.drop_duplicates().astype('str').to_dict(orient='records')
    result = []
    if not_found_cities:
        result = cities_not_found(result, not_found_cities, df_of_cities)
    else:
        result = cities_found(result, df_of_cities)
    return result


def compare_cities(url_cities):
    city1, city2 = url_cities_to_two_cities(url_cities)
    df_of_cities, not_found_cities = check_df_for_cities([city1, city2], True)
    list_of_dicts_cities_info = df_of_cities.astype('str').to_dict(orient='records')
    result = []
    if not_found_cities:
        result = cities_not_found(result, not_found_cities, list_of_dicts_cities_info)
    else:
        result = cities_found(result, list_of_dicts_cities_info)
        comparison_info = dict(
            {'Comparison': [diff_latitude(df_of_cities, city1, city2), diff_timezone(df_of_cities, city1, city2)]})
        result.append(comparison_info)
    return result


def check_df_for_cities(cities, first_only: bool):
    df_of_cities = pd.DataFrame()
    not_found_cities = []
    df_to_apply_mask = table.loc[table['feature class'] == 'P']
    for city in cities:
        city_lower = city.lower()
        df_of_cities_with_such_name = df_to_apply_mask.loc[(new_table['allnames'].apply(lambda x: city_lower in x))]
        if df_of_cities_with_such_name.empty:
            not_found_cities.append(city)
        else:
            if first_only:
                df_of_cities = pd.concat(
                    [df_of_cities, df_of_cities_with_such_name.sort_values(by=['population'], ascending=False).head(1)])
            else:
                df_of_cities = pd.concat(
                    [df_of_cities, df_of_cities_with_such_name.sort_values(by=['population'], ascending=False)])
    return df_of_cities, not_found_cities


def cities_not_found(result, not_found_cities, df_of_cities):
    result_failed_dict = dict()
    not_found_dict = dict({"Sorry, there is no info about city/cities": list(dict.fromkeys(not_found_cities))})
    suggestions_dict = dict()
    for city in not_found_cities:
        suggestions_dict.update(
            {"Perhaps you wanted to enter a different word instead of " + "'" + city + "'": find_closest(city)})
    not_found_dict.update({"Suggestions": suggestions_dict})
    result_failed_dict.update({"Search failed": not_found_dict})
    result.append(result_failed_dict)
    if df_of_cities:
        cities_dict = dict()
        cities_dict.update({"Cities": df_of_cities})
        result.append(cities_dict)
    return result


def cities_found(result, df_of_cities):
    cities_dict = dict()
    cities_dict.update({"Cities": df_of_cities})
    result.append(cities_dict)
    return result


def url_cities_to_list_of_cities(cities):
    return [str(city).strip() for city in cities.split(',')]


def url_cities_to_two_cities(cities):
    cities = [str(city).strip() for city in cities.split(',')]
    return cities[0], cities[1]


def diff_latitude(df, city1, city2):
    df.reset_index(inplace=True)
    city_1_lat = df.loc[0, 'latitude']
    city_2_lat = df.loc[1, 'latitude']
    if city_1_lat > city_2_lat:
        result = dict({city1 + " is located North of " + city2 + " at": str(
            round(city_1_lat - city_2_lat, 3)) + " degrees latitude"})
    elif city_1_lat < city_2_lat:
        result = dict({city2 + " is located North of " + city1 + " at": str(
            round(city_2_lat - city_1_lat, 3)) + " degrees latitude"})
    else:
        result = dict({city1 + " and " + city2 + " has the same latitude": str(round(city_1_lat, 3))})
    return result


def diff_timezone(df, city1, city2):
    df.reset_index(inplace=True)
    city_1_tz = datetime.datetime.now(pytz.timezone(df.loc[0, 'timezone'])).utcoffset().total_seconds() / 60 / 60
    city_2_tz = datetime.datetime.now(pytz.timezone(df.loc[1, 'timezone'])).utcoffset().total_seconds() / 60 / 60
    diff = abs(float(city_1_tz - city_2_tz))
    if diff == 0.0:
        result = dict({city1 + " and " + city2 + " has the same timezone": df.loc[0, 'timezone']})
    else:
        result = dict({"The difference of timezones is": diff})
    return result


def find_closest(city):
    return [list(map(str.title, difflib.get_close_matches(city, uniq_words, n=10, cutoff=0.6)))][0]
