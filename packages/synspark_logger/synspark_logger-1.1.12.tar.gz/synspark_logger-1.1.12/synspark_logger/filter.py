import re

from synspark_logger.output import log


class Filter:
    # builting
    def __init__(self, name='NO_NAME'):
        """Init filter

        :param name: name of filter (for identifiate / debug)
        """
        self.name = name
        self.__message_rules = {}  # message's filter
        self.__min_criticity = -1  # to allow (disable by default)
        self.__syslog_facility = []

    def __len__(self):
        """Get number of rules

        :return: rules len
        """
        return len(self.__message_rules) + len(self.__syslog_facility) + \
               (1 if self.__min_criticity >= 0 else 0)  # min criticity are set ?

    def __repr__(self):
        """Get object representation"""
        return '<%s(%s) size=%d>' % (self.__class__.__name__, self.name, len(self))

    # public method
    def add_message_rule(self, rule):
        """ Add a filter string

        :param rule: string rule (for message check)
        """
        filter_type, filter_rule = rule.split(':', 1)

        if filter_type not in self.__message_rules:
            self.__message_rules[filter_type] = []

        # compile regex filters
        if 'regex' in filter_type:
            filter_rule = re.compile(filter_rule)

        self.__message_rules[filter_type].append(filter_rule)

    def add_syslog_facility(self, *args):
        """Add syslog facility (for syslog facility check)

        :param args: list of syslog facility (id)
        """
        self.__syslog_facility += args

    def check(self, message=None, criticity=None, syslog_facility=None):
        """Check if it's allowned to sent to api

        :param message: value string to check
        :param criticity: criticity name
        :return: is allowned
        """
        return self.is_empty() or \
               (message is None or self.__check_message(message)) and \
               (criticity is None or self.__check_criticity(criticity)) and \
               (syslog_facility is None or self.__check_syslog_facility(syslog_facility))

    def is_empty(self):
        """This filter is empty ? (no rule)

        :return: is empty boolean
        """
        return len(self) == 0

    # private method

    def set_min_criticity(self, criticity):
        """ set the minimum level to send to api

        :param criticity: criticity name
        """
        self.__min_criticity = self.__get_criticity_value(criticity)

    def __check_criticity(self, criticity):
        """Check if criticity is allowned to sent to api

        :param criticity: criticity name
        :return: is allowned
        """
        return self.__min_criticity >= self.__get_criticity_value(criticity)

    def __check_message(self, message):
        """Check if value is allowned to sent to api (apply filter rules)

        :param message: value string to check
        :return: is allowned
        """
        if not self.__message_rules:  # no filter
            return False

        for filter_type in self.__message_rules:
            check_handler = {
                'contain':      lambda filter: filter in message,
                'end_with':     lambda filter: message.endswith(filter),
                'regex':        lambda filter: filter.search(message),
                'start_with':   lambda filter: message.startswith(filter),
            }.get(filter_type)

            # unknown filter type
            if not check_handler:
                log.error('%s: %s unknown' % (self, filter_type))
                continue

            # filter check
            for filter in self.__message_rules[filter_type]:
                if check_handler(filter):
                    return True

    def __check_syslog_facility(self, syslog_facility):
        return syslog_facility in self.__syslog_facility

    def __get_criticity_value(self, criticity):
        """Get (syslog) criticity code

        :param criticity: criticity name
        :return: criticity int code
        """
        criticity = {
            'EMERGENCY':    0,
            'ALERT':        1,
            'CRITICAL':     2,
            'ERROR':        3,
            'WARNING':      4,
            'NOTICE':       5,
        }.get(str(criticity).upper(), criticity)

        if isinstance(criticity, int):
            return criticity

        raise TypeError('%s: criticity "%s" in unknown' % (self, criticity))
