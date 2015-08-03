import json
import datetime
from phitime.exceptions import AvailableTimeParseException
from phitime.models import AvailableTime


class MemberHelper:
    @staticmethod
    def gen_available_times(event, member, active_times_json_str):
        """
        :type event: phitime.models.Event
        :type member: phitime.models.Member 
        :type post_active_times: str
        :rtype: list[phitime.models.AvailableTime]
        :exception: AvailableTimeParseException, phitime.exceptions.ValidationException
        """
        available_period_list = []
        """list[phitime.models.AvailableTime]"""
        data = json.loads(active_times_json_str)
        if not isinstance(data, dict):
            raise AvailableTimeParseException('invalid active time json')
        for the_date_str in data.keys():
            try:
                the_date = datetime.datetime.strptime(the_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise AvailableTimeParseException('invalid active time key format, not "%Y-%m-%d"')

            # TODO validate available_date in period event specified

            available_period_data = data.get(the_date_str)
            if not isinstance(available_period_data, list):
                raise AvailableTimeParseException('invalid active time json')

            for period_data in available_period_data:
                if not isinstance(period_data, dict):
                    raise AvailableTimeParseException('invalid active time json')
                start_minutes = period_data.get('startMinutes')
                length = period_data.get('periodLength')

                period = AvailableTime(member, the_date, start_minutes, length)
                available_period_list.append(period)
        return available_period_list
