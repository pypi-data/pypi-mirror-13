from hitchtest.environment import checks
from hitchserve import Service
from os.path import join
import signal
import shutil
import sys

class ElasticService(Service):
    def __init__(self, elastic_package, **kwargs):
        self.elastic_package = elastic_package
        checks.freeports([9200, 9300, ])
        kwargs['log_line_ready_checker'] = lambda line: "started" in line
        kwargs['no_libfaketime'] = True
        super(ElasticService, self).__init__(**kwargs)

    @Service.command.getter
    def command(self):
        if self._command is None:
            return [
                      self.elastic_package.elasticsearch,
                      "--path.data={}".format(join(
                        self.service_group.hitch_dir.hitch_dir, 'elasticdata'
                      )),
                      "--path.tmp={}".format(join(
                        self.service_group.hitch_dir.hitch_dir, 'elastictmp'
                      )),
                      "--path.conf={}".format(join(
                        self.service_group.hitch_dir.hitch_dir, 'elasticconf'
                      )),
                   ]
        else:
            return self._command
