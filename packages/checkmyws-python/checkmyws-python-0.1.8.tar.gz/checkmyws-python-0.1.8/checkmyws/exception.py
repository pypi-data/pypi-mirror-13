# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


class CheckmywsError(Exception):

    def __init__(self, response):
        self.status_code = response.status_code
        self.reason = response.reason
        self.url = response.url

        super(CheckmywsError, self).__init__(self.__str__())

    def __repr__(self):
        msg = "CheckmywsError '{0}': HTTP {1} - {2}".format(
            self.url,
            self.status_code,
            self.reason
        )

        logger.debug(msg)
        return msg

    def __str__(self):
        return self.__repr__()
