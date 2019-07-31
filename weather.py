
import requests
import bs4


class Gismeteo:

    def __init__(self):
        self.now = self.get_weather('now')
        self.today = self.get_weather()
        self.tomorrow = self.get_weather('tomorrow')

    def get_weather(self, day=''):

        url = 'https://www.gismeteo.ru/weather-irkutsk-4787/'

        if day in ('now', 'tomorrow'):
            url += day

        response = requests.get(url, headers={"User-Agent": "Firefox/68.0"})
        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        tags = soup.select('div.tab.tooltip span.unit.unit_temperature_c')

        if len(tags) == 1:
            return tags[0].text.strip(), ''
        elif len(tags) == 2:
            return tags[0].text.strip(), tags[1].text.strip()

        return '', ''
