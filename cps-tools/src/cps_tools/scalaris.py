
from .service import ServiceCmd


class ScalarisCmd(ServiceCmd):

    def __init__(self, parser, client):
        ServiceCmd.__init__(self, parser, client, "scalaris", ['scalaris'],
                            "Scalaris service sub-commands help")
