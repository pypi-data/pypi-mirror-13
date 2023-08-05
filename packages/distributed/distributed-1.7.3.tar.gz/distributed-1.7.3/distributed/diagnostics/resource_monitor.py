from toolz import get
from tornado import gen

from ..core import connect, read, write, rpc
from ..utils import ignoring, is_kernel, key_split
from ..executor import default_executor
from ..scheduler import Scheduler

with ignoring(ImportError):
    from bokeh.plotting import figure, Figure, show, output_notebook, ColumnDataSource
    from bokeh.models import HoverTool, LinearAxis, Range1d
    from bokeh.io import curstate, push_notebook


class ResourceMonitor(object):
    """ Display current CPU and Memory resources on each worker

    Parameters
    ----------
    addr: tuple, optional
        (ip, port) of scheduler.  Defaults to scheduler of recent Executor
    interval: Number, optional
        Interval between updates.  Defaults to 1s
    """
    def __init__(self, addr=None, interval=1.00):
        if addr is None:
            scheduler = default_executor().scheduler
            if isinstance(scheduler, rpc):
                addr = (scheduler.ip, scheduler.port)
            elif isinstance(scheduler, Scheduler):
                addr = ('127.0.0.1', scheduler.port)

        self.cds = ColumnDataSource({k: []
            for k in ['host', 'cpu', 'memory',
                      'zero', 'left', 'mid', 'right']})

        self.display_notebook = False


        self.figure = figure(height=200, width=800, y_range=(0, 100))
        self.figure.logo = None

        cpu = self.figure.quad(legend='cpu', left='left', right='mid',
                         bottom='zero', top='cpu', source=self.cds,
                         color=(0, 0, 255, 0.5))
        memory = self.figure.quad(legend='memory', left='mid', right='right',
                         bottom='zero', top='memory', source=self.cds,
                         color=(255, 0, 0, 0.5))

        self.figure.add_tools(HoverTool(renderers=[cpu, memory],
                                        tooltips=[("host", "@host"),
                                                  ("cpu", "@cpu"),
                                                  ("memory", "@memory")]))

        self.future = self.update(addr, interval)

        if is_kernel() and not curstate().notebook:
            output_notebook()
            assert curstate().notebook

    def _ipython_display_(self, **kwargs):
        show(self.figure)
        self.display_notebook = True

    @gen.coroutine
    def update(self, addr, interval):
        """ Query the Scheduler, update the figure

        This opens a connection to the scheduler, sends it a function to run
        periodically, streams the results back and uses those results to update
        the bokeh figure
        """
        self.stream = yield connect(*addr)

        def func(scheduler):
            """ Get CPU and Memory usage on each worker """
            workers = [k for k, v in sorted(scheduler.ncores.items(),
                                            key=lambda x: x[0], reverse=True)]
            nannies = [(ip, scheduler.nannies[(ip, port)])
                       for ip, port in workers]
            dicts = [get(-1, scheduler.resource_logs[w], dict())
                     for w in nannies]

            return {'workers': workers,
                    'cpu': [d.get('cpu_percent', -1) for d in dicts],
                    'memory': [d.get('memory_percent', -1) for d in dicts]}

        yield write(self.stream, {'op': 'feed',
                                  'function': func,
                                  'interval': interval})
        while True:
            try:
                response = yield read(self.stream)
            except Exception:
                break

            self.cds.data['host'] = [host for host, port in response['workers']]
            self.cds.data['cpu'] = response['cpu']
            self.cds.data['memory'] = response['memory']

            n = len(response['workers'])

            self.cds.data['zero'] = [0] * n
            self.cds.data['left'] = [i + 0.00 for i in range(n)]
            self.cds.data['mid'] = [i + 0.50 for i in range(n)]
            self.cds.data['right'] = [i + 1.00 for i in range(n)]

            if self.display_notebook:
                push_notebook()


class Occupancy(object):
    """ Display the tasks running and waiting on each worker

    Parameters
    ----------
    addr: tuple, optional
        (ip, port) of scheduler.  Defaults to scheduler of recent Executor
    interval: Number, optional
        Interval between updates.  Defaults to 1s
    """
    def __init__(self, addr=None, interval=1.00):
        if addr is None:
            scheduler = default_executor().scheduler
            if isinstance(scheduler, rpc):
                addr = (scheduler.ip, scheduler.port)
            elif isinstance(scheduler, Scheduler):
                addr = ('127.0.0.1', scheduler.port)

        self.cds = ColumnDataSource({k: []
            for k in ['host', 'processing', 'stacks', 'waiting',
                      'zero', 'left', 'mid', 'right']})

        self.display_notebook = False


        left_range = Range1d(0, 1)
        self.figure = figure(height=200, width=800, y_range=left_range)
        self.figure.extra_y_ranges = {'waiting': Range1d(start=0, end=1)}
        self.figure.add_layout(LinearAxis(y_range_name='waiting',
                                          axis_label='waiting'), 'right')
        self.figure.logo = None

        proc = self.figure.quad(legend='processing', left='left', right='mid',
                              bottom='zero', top='nprocessing', source=self.cds,
                              color=(0, 0, 255, 0.5))
        wait = self.figure.quad(legend='waiting', left='mid', right='right',
                              bottom='zero', top='waiting', source=self.cds,
                              y_range_name='waiting', color=(255, 0, 0, 0.5))

        self.figure.add_tools(HoverTool(renderers=[proc, wait],
                                        tooltips=[("host", "@host"),
                                                  ("processing", "@processing"),
                                                  ("waiting", "@waiting")]))

        self.future = self.update(addr, interval)

        if is_kernel() and not curstate().notebook:
            output_notebook()
            assert curstate().notebook

    def _ipython_display_(self, **kwargs):
        show(self.figure)
        self.display_notebook = True

    @gen.coroutine
    def update(self, addr, interval):
        """ Query the Scheduler, update the figure

        This opens a connection to the scheduler, sends it a function to run
        periodically, streams the results back and uses those results to update
        the bokeh figure
        """
        self.stream = yield connect(*addr)

        def func(scheduler):
            """ Get tasks running or waiting on each worker """
            workers = [k for k, v in sorted(scheduler.ncores.items(),
                                            key=lambda x: x[0], reverse=True)]
            processing = [list(map(key_split, scheduler.processing[w]))
                          for w in workers]
            nprocessing = list(map(len, processing))
            nstacks = [len(scheduler.stacks[w]) for w in workers]

            return {'host': [host for host, port in workers],
                    'processing': processing,
                    'nprocessing': nprocessing,
                    'waiting': nstacks}

        yield write(self.stream, {'op': 'feed',
                                  'function': func,
                                  'interval': interval})
        while True:
            try:
                response = yield read(self.stream)
            except Exception:
                break

            self.cds.data.update(response)

            n = len(response['host'])

            self.figure.y_range.end = max(self.figure.y_range.end,
                                          *response['nprocessing'])
            self.figure.extra_y_ranges['waiting'].end = \
                    max(self.figure.extra_y_ranges['waiting'].end,
                        *response['waiting'])

            self.cds.data['zero'] = [0] * n
            self.cds.data['left'] = [i + 0.00 for i in range(n)]
            self.cds.data['mid'] = [i + 0.50 for i in range(n)]
            self.cds.data['right'] = [i + 1.00 for i in range(n)]

            if self.display_notebook:
                push_notebook()
