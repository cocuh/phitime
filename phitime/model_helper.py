import json
import datetime
from phitime.exceptions import TimetablePeriodsParseException
from phitime.models import AvailableTime, ProposedTime


class EventHelper:
    @staticmethod
    def gen_proposed_times(event, proposed_times_json_str):
        """
        :type event: phitime.models.Event
        :type proposed_times_json_str: str 
        :rtype: list[phitime.models.ProposedTime]
        """
        proposed_time_list = []
        data = json.loads(proposed_times_json_str)
        if not isinstance(data, dict):
            raise TimetablePeriodsParseException('invalid json format')
        for the_date_str in data.keys():
            try:
                the_date = datetime.datetime.strptime(the_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise TimetablePeriodsParseException('invalid active time key format, not "%Y-%m-%d"')
            # TODO validate available_date in period event specified

            proposed_time_data = data.get(the_date_str)
            if not isinstance(proposed_time_data, list):
                raise TimetablePeriodsParseException('invalid json format')

            for time_data in proposed_time_data:
                if not isinstance(time_data, dict):
                    raise TimetablePeriodsParseException('invalid json format')
                start_minutes = time_data.get('startMinutes')
                length = time_data.get('periodLength')

                proposed_time = ProposedTime(event, the_date, start_minutes, length)
                proposed_time_list.append(proposed_time)
        return proposed_time_list


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
        available_time_list = []
        """list[phitime.models.AvailableTime]"""
        data = json.loads(active_times_json_str)
        if not isinstance(data, dict):
            raise TimetablePeriodsParseException('invalid json format')
        for the_date_str in data.keys():
            try:
                the_date = datetime.datetime.strptime(the_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise TimetablePeriodsParseException('invalid active time key format, not "%Y-%m-%d"')

            # TODO validate available_date in period event specified

            available_period_data = data.get(the_date_str)
            if not isinstance(available_period_data, list):
                raise TimetablePeriodsParseException('invalid json format')

            for period_data in available_period_data:
                if not isinstance(period_data, dict):
                    raise TimetablePeriodsParseException('invalid json format')
                start_minutes = period_data.get('startMinutes')
                length = period_data.get('periodLength')

                period = AvailableTime(member, the_date, start_minutes, length)
                available_time_list.append(period)
        return available_time_list
