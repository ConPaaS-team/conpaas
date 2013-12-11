from .service import ServiceCmd


class SeleniumCmd(ServiceCmd):

    def __init__(self, selenium_parser, client):
        ServiceCmd.__init__(self, selenium_parser, client, "selenium",
                            ['node'], "Selenium service sub-commands help")
