from phitime.models import AvailableTime, ProposedTime
from collections import Iterable


class BaseStrategy():
    def __init__(self, event, member):
        """
        :type event: phitime.models.Event
        :type member: phitime.models.Member
        :return:
        """
        self.event = event
        """:type: phitime.models.Event"""
        self.member = member
        """:type: phitime.models.Member"""

    def gen_period_classes(self, period):
        """
        :type period: phitime.timetable.base.SVGPeriod
        :rtype: list[str]
        """
        pass

    def gen_day_classes(self, day):
        """
        :type day: phitime.timetable.base.SVGDay
        :return: list[str]
        """
        pass


class _ProposedTimeMixin():
    @staticmethod
    def _gen_proposed_time_dic_group_by_date(event):
        # fixme! using group_by in sqlalchemy
        res = {}
        proposed_time_list = ProposedTime.query.filter_by(event=event).all()
        for proposed_time in proposed_time_list:
            if proposed_time.date in res:
                res[proposed_time.date].append(proposed_time)
            else:
                res[proposed_time.date] = [proposed_time]
        return res


class _AvailableTimePeriod():
    @staticmethod
    def _gen_available_time_dic_group_by_date(member):
        # fixme! using group_by in sqlalchemy
        res = {}
        available_time_list = AvailableTime.query.filter(AvailableTime.member == member).all()
        for available_time in available_time_list:
            if available_time.date in res:
                res[available_time.date].append(available_time)
            else:
                res[available_time.date] = [available_time]
        return res


class IsTheMemberAvailable(BaseStrategy, _AvailableTimePeriod):
    def __init__(self, *args):
        super().__init__(*args)
        self.available_time_dic = self._gen_available_time_dic_group_by_date(self.member)
        """:type: dict[datetime.date, phitime.models.AvailableTime]"""

    def gen_period_classes(self, period):
        """
        :type period: phitime.timetable.base.SVGPeriod
        :rtype: list[str]
        """
        if self._is_active_period(period):
            return ["active"]
        else:
            return []

    def _is_active_period(self, period):
        the_day_available_times = self.available_time_dic.get(period.date.date(), [])
        """:type: list[phitime.models.AvailableTime]"""
        for available_time in the_day_available_times:
            if available_time.get_end_time() <= period.start_y:
                continue
            elif period.end_y <= available_time.get_start_time():
                continue
            else:
                return True
        return False


class IsTheEventProposed(BaseStrategy, _ProposedTimeMixin):
    def __init__(self, *args):
        super().__init__(*args)
        self.proposed_time_dic = self._gen_proposed_time_dic_group_by_date(self.event)
        """:type: dict[datetime.date, phitime.models.ProposedTime]"""

    def gen_period_classes(self, period):
        """
        :type period: phitime.timetable.base.SVGPeriod
        :rtype: list[str]
        """
        if self._is_active_period(period):
            return ["active"]
        else:
            return []

    def _is_active_period(self, period):
        the_day_proposed_times = self.proposed_time_dic.get(period.date.date(), [])
        """:type: list[phitime.models.ProposedTime]"""
        for proposed_time in the_day_proposed_times:
            if proposed_time.get_end_time() <= period.start_y:
                continue
            elif period.end_y <= proposed_time.get_start_time():
                continue
            else:
                return True
        return False


class IsUnavailable(BaseStrategy, _ProposedTimeMixin):
    def __init__(self, *args):
        super().__init__(*args)
        self.proposed_time_dic = self._gen_proposed_time_dic_group_by_date(self.event)
        """:type: dict[datetime.date, phitime.models.ProposedTime]"""

    def gen_period_classes(self, period):
        """
        :type period: phitime.timetable.base.SVGPeriod
        :rtype: list[str]
        """
        if self._is_proposed_period(period):
            return []
        else:
            return ["unavailable"]

    def _is_proposed_period(self, period):
        the_day_proposed_times = self.proposed_time_dic.get(period.date.date(), [])
        """:type: list[phitime.models.ProposedTime]"""
        for proposed_time in the_day_proposed_times:
            if proposed_time.get_end_time() <= period.start_y:
                continue
            elif period.end_y <= proposed_time.get_start_time():
                continue
            else:
                return True
        return False


class AvailableMember(BaseStrategy, _AvailableTimePeriod):
    def __init__(self, *args):
        super().__init__(*args)
        self.data = {
            member: self._gen_available_time_dic_group_by_date(member)
            for member in self.event.members
            }
        self.member_num = len(self.event.members)

    def gen_period_classes(self, period):
        active_member = [
            member
            for member in self.data.keys()
            if self.is_the_member_active(member, period)
            ]
        percent = "active-percent-{:02d}".format(int(len(active_member) * 100 / self.member_num))
        return [
                   percent,
               ] + [
                   'active-member-{}'.format(member.position)
                   for member in active_member
                   ]

    def is_the_member_active(self, member, period):
        the_day_available_times = self.data[member].get(period.date.date(), [])
        for available_time in the_day_available_times:
            if available_time.get_start_time() <= period.start_y \
                    and period.end_y <= available_time.get_end_time():
                return True
        return False


class ClassStrategies:
    is_the_member_available = IsTheMemberAvailable
    is_the_event_proposed = IsTheEventProposed
    is_unavailable = IsUnavailable
    available_member = AvailableMember


class ClassStrategyList():
    def __init__(self, strategy_list, event=None, member=None):
        """
        :type strategy_list: list[BaseStrategy.__class__]
        :type event: phitime.models.Event
        :type member: phitime.models.Member
        :return:
        """
        self.event = event
        self.member = member
        self.strategy_list = [
            strategy_class(self.event, self.member)
            for strategy_class in strategy_list
            ]
        """:type: list[BaseStrategy]"""

    def copy(self, event=None):
        return ClassStrategyList(self.strategy_list, event)

    def gen_period_classes(self, period):
        classes = set()
        for strategy in self.strategy_list:
            the_classes = strategy.gen_period_classes(period)
            if the_classes and isinstance(the_classes, Iterable):
                classes.update(set(the_classes))
        return classes

    def gen_day_classes(self, day):
        classes = set()
        for strategy in self.strategy_list:
            the_classes = strategy.gen_day_classes(day)
            if the_classes and isinstance(the_classes, Iterable):
                classes.update(set(the_classes))
        return classes


__all__ = [
    'ClassStrategies',
    'ClassStrategyList',
]
