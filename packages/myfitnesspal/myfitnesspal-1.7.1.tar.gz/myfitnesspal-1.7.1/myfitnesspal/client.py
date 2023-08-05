import datetime
import os.path
import re

import lxml.html
from measurement.measures import Energy, Weight, Volume
import requests
from collections import OrderedDict

from .base import MFPBase
from .day import Day
from .entry import Entry
from .keyring_utils import get_password_from_keyring
from .meal import Meal


class Client(MFPBase):
    BASE_URL = 'http://www.myfitnesspal.com/'
    BASE_URL_SECURE = 'https://www.myfitnesspal.com/'
    LOGIN_PATH = 'account/login'
    ABBREVIATIONS = {
        'carbs': 'carbohydrates',
    }
    DEFAULT_MEASURE_AND_UNIT = {
        'calories': (Energy, 'Calorie'),
        'carbohydrates': (Weight, 'g'),
        'fat': (Weight, 'g'),
        'protein': (Weight, 'g'),
        'sodium': (Weight, 'mg'),
        'sugar': (Weight, 'g'),
    }

    def __init__(self, username, password=None, login=True, unit_aware=False):
        self.username = username
        if password is None:
            password = get_password_from_keyring(self.username)
        self.__password = password
        self.unit_aware = unit_aware

        self.session = requests.Session()
        if login:
            self._login()

    def _login(self):
        login_url = os.path.join(self.BASE_URL_SECURE, self.LOGIN_PATH)
        document = self._get_document_for_url(login_url)
        authenticity_token = document.xpath(
            "(//input[@name='authenticity_token']/@value)[1]"
        )[0]
        utf8_field = document.xpath(
            "(//input[@name='utf8']/@value)[1]"
        )[0]

        result = self.session.post(
            login_url,
            data={
                'utf8': utf8_field,
                'authenticity_token': authenticity_token,
                'username': self.username,
                'password': self.__password,
            }
        )
        # result.content is bytes so we decode it ASSUMING utf8 (which may be a
        # bad assumption?) PORTING_CHECK
        content = result.content.decode('utf8')
        if 'Incorrect username or password' in content:
            raise ValueError(
                "Incorrect username or password."
            )

    def _get_full_name(self, raw_name):
        name = raw_name.lower()
        if name not in self.ABBREVIATIONS:
            return name
        return self.ABBREVIATIONS[name]

    def _get_url_for_date(self, date, username):
        return os.path.join(
            self.BASE_URL,
            'food/diary/',
            username
        ) + '?date=%s' % (
            date.strftime('%Y-%m-%d')
        )

    def _get_url_for_measurements(self, page=1, measurement_id=1):
        return os.path.join(
            self.BASE_URL,
            'measurements/edit'
        ) + '?page=%d&type=%d' % (page, measurement_id)

    def _get_content_for_url(self, url):
        return self.session.get(url).content.decode('utf8')

    def _get_document_for_url(self, url):
        content = self._get_content_for_url(url)

        return lxml.html.document_fromstring(content)

    def _get_measurement(self, name, value):
        if not self.unit_aware:
            return value
        measure, kwarg = self.DEFAULT_MEASURE_AND_UNIT[name]
        return measure(**{kwarg: value})

    def _get_numeric(self, string, flt=False):
        if flt:
            return float(re.sub(r'[^\d.]+', '', string))
        else:
            return int(re.sub(r'[^\d.]+', '', string))

    def _get_fields(self, document):
        meal_header = document.xpath("//tr[@class='meal_header']")[0]
        tds = meal_header.findall('td')
        fields = ['name']
        for field in tds[1:]:
            fields.append(
                self._get_full_name(
                    field.text
                )
            )
        return fields

    def _get_goals(self, document):
        total_header = document.xpath("//tr[@class='total']")[0]
        goal_header = total_header.getnext()  # The following TR contains goals
        columns = goal_header.findall('td')

        fields = self._get_fields(document)

        nutrition = {}
        for n in range(1, len(columns)):
            column = columns[n]
            try:
                nutr_name = fields[n]
            except IndexError:
                # This is the 'delete' button
                continue
            value = self._get_numeric(column.text)
            nutrition[nutr_name] = self._get_measurement(nutr_name, value)

        return nutrition

    def _get_meals(self, document):
        meals = []
        fields = None
        meal_headers = document.xpath("//tr[@class='meal_header']")

        for meal_header in meal_headers:
            tds = meal_header.findall('td')
            meal_name = tds[0].text.lower()
            if fields is None:
                fields = self._get_fields(document)
            this = meal_header
            entries = []

            while True:
                this = this.getnext()
                if not this.attrib.get('class') is None:
                    break
                columns = this.findall('td')

                # When viewing a friend's diary, the HTML entries containing the
                # actual food log entries are different: they don't contain an
                # embedded <a/> element but rather the food name directly.
                if columns[0].find('a') is None:
                    name = columns[0].text.strip()
                else:
                    name = columns[0].find('a').text

                nutrition = {}

                for n in range(1, len(columns)):
                    column = columns[n]
                    try:
                        nutr_name = fields[n]
                    except IndexError:
                        # This is the 'delete' button
                        continue
                    value = self._get_numeric(column.text)
                    nutrition[nutr_name] = self._get_measurement(
                        nutr_name,
                        value
                    )

                entries.append(
                    Entry(
                        name,
                        nutrition,
                    )
                )

            meals.append(
                Meal(
                    meal_name,
                    entries,
                )
            )

        return meals

    def get_date(self, *args, **kwargs):
        if len(args) == 3:
            date = datetime.date(
                int(args[0]),
                int(args[1]),
                int(args[2]),
            )
        elif len(args) == 1 and isinstance(args[0], datetime.date):
            date = args[0]
        else:
            raise ValueError(
                'get_date accepts either a single datetime or date instance, '
                'or three integers representing year, month, and day '
                'respectively.'
            )
        document = self._get_document_for_url(
            self._get_url_for_date(
                date,
                kwargs.get('username', self.username)
            )
        )

        meals = self._get_meals(document)
        goals = self._get_goals(document)
        notes = self._get_notes(document)
        water = self._get_water(document)

        day = Day(
            date=date,
            meals=meals,
            goals=goals,
            notes=notes,
            water=water
        )

        return day

    def get_measurements(
        self, measurement='Weight', lower_bound=None, upper_bound=None
    ):
        """ Returns measurements of a given name between two dates."""
        if upper_bound is None:
            upper_bound = datetime.date.today()
        if lower_bound is None:
            lower_bound = upper_bound - datetime.timedelta(days=30)

        # If they entered the dates in the opposite order, let's
        # just flip them around for them as a convenience
        if lower_bound > upper_bound:
            lower_bound, upper_bound = upper_bound, lower_bound

        # get the URL for the main check in page
        document = self._get_document_for_url(
            self._get_url_for_measurements()
        )

        # gather the IDs for all measurement types
        measurement_ids = self._get_measurement_ids(document)

        # select the measurement ID based on the input
        if measurement in measurement_ids.keys():
            measurement_id = measurement_ids[measurement]
        else:
            raise ValueError(
                "Measurement '%s' does not exist." % measurement
            )

        page = 1
        measurements = OrderedDict()

        # retrieve entries until finished
        while True:
            # retrieve the HTML from MyFitnessPal
            document = self._get_document_for_url(
                self._get_url_for_measurements(page, measurement_id)
            )

            # parse the HTML for measurement entries and add to dictionary
            results = self._get_measurements(document)
            measurements.update(results)

            # stop if there are no more entries
            if len(results) == 0:
                break

            # continue if the lower bound has not been reached
            elif list(results.keys())[-1] > lower_bound:
                page += 1
                continue

            # otherwise stop
            else:
                break

        # remove entries that are not within the dates specified
        for date in list(measurements.keys()):
            if not upper_bound >= date >= lower_bound:
                del measurements[date]

        return measurements

    def _get_measurements(self, document):

        # find the tr element for each measurement entry on the page
        trs = document.xpath("//table[contains(@class,'check-in')]/tbody/tr")

        measurements = OrderedDict()

        # create a dictionary out of the date and value of each entry
        for entry in trs:

            # ensure there are measurement entries on the page
            if len(entry) == 1:
                return measurements
            else:
                measurements[entry[1].text] = entry[2].text

        temp_measurements = OrderedDict()

        # converts the date to a datetime object and the value to a float
        for date in measurements:
            temp_measurements[
                datetime.datetime.strptime(date, '%m/%d/%Y').date()
            ] = self._get_numeric(measurements[date], flt=True)

        measurements = temp_measurements

        return measurements

    def _get_measurement_ids(self, document):

        # find the option element for all of the measurement choices
        options = document.xpath("//select[@id='type']/option")

        ids = {}

        # create a dictionary out of the text and value of each choice
        for option in options:
            ids[option.text] = int(option.attrib.get('value'))

        return ids

    def _get_notes(self, document):
        notes_header = document.xpath("//p[@class='note']")[0]
        header_text = [notes_header.text] if notes_header.text else []
        lines = header_text + list(map(lambda x: x.tail, notes_header))
        return '\n'.join([l.strip() for l in lines])

    def _get_water(self, document):
        water_header = document.xpath("//div[@class='water-counter']/p/a")[0]
        try:
            cups = int(water_header.tail.strip())
            if self.unit_aware:
                return Volume(us_cup=cups)
            return cups
        except (ValueError, TypeError):
            return None

    def __unicode__(self):
        return u'MyFitnessPal Client for %s' % self.username
