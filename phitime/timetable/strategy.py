class BaseStrategy():
    def __init__(self, event):
        """
        :type event: phitime.models.Event
        :return:
        """
        self.event = event
        """:type: phitime.models.Event"""

    def gen_period_classes(self, period):
        """
        :type period: phitime.timetable.base.SVGPeriod
        :rtype: list[str]
        """
        pass

    def gen_day_classes(self, day):
        """
        :type day: phitime.timetable.base.SVGDay
        :return:
        """
        pass


class IsActive(BaseStrategy):
    def gen_period_classes(self, period):
        pass


class ClassStrategies:
    is_active = IsActive


class ClassStrategyList():
    def __init__(self, strategy_list, event=None):
        self.strategy_list = strategy_list
        """:type: list[BaseStrategy]"""
        self.event = event

    def copy(self, event=None):
        return ClassStrategyList(self.strategy_list, event)

    def gen_period_classes(self, period):
        classes = {}
        for strategy in self.strategy_list:
            classes.update(strategy.gen_period_classes(period))
        return classes

    def gen_day_classes(self, day):
        classes = {}
        for strategy in self.strategy_list:
            classes.update(strategy.gen_day_classes(day))
        return classes


__all__ = [
    'ClassStrategies',
    'ClassStrategyList',
]
