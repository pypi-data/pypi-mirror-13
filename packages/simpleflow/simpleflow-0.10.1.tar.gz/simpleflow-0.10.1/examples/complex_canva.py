import time

from simpleflow import (
    activity,
    futures,
    Workflow,
)
from simpleflow.canvas import Group, Chain
from simpleflow.task import ActivityTask


@activity.with_attributes(task_list='example', version='example')
def wait(task_name, x):
    print "started task: {}".format(task_name)
    time.sleep(x)
    print "finished task: {}".format(task_name)


class ExampleWorkflow(Workflow):
    name = 'canvas'
    version = 'example'
    task_list = 'example'

    def run_old(self):
        a = self.submit(wait, "A", 1)
        b = ....
        print "foo"
