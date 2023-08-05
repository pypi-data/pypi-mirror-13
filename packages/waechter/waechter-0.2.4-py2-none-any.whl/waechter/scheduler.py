# Waechter - Job Scheduling Helper
# Copyright (C) 2016  Lukas Rist

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import tempfile
import fcntl
import psutil

from collections import defaultdict


try:
    perf_counter = time.perf_counter
except AttributeError:
    perf_counter = time.clock


class BaseJob(object):
    def __init__(self, interval=5):
        self.interval = interval


class JobScheduler(object):

    def __init__(self):
        # initialize all the jobs
        self.job_instances = [job_instance() for job_instance in BaseJob.__subclasses__()]

    @classmethod
    def job_spawner(cls, job_instance, **kwargs):

        def del_lock():
            if os.path.isfile(lock_file):
                os.remove(lock_file)

        pid = os.fork()
        if pid == 0:
            # child
            file_name = job_instance.__class__.__name__
            lock_file = os.path.sep.join([tempfile.gettempdir(), file_name])
            with open(lock_file, 'w') as lock:
                try:
                    fcntl.lockf(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    job_instance.work(**kwargs)
                    del_lock()
                except IOError as e:
                    print('Lock file {} has error {}'.format(lock_file, e))
                except KeyboardInterrupt:
                    del_lock()
            # exit the fork
            sys.exit()
        else:
            return pid

    @classmethod
    def _reap_pids(cls, worker_pids):
        terminated_zombies = set()
        for pid in worker_pids:
            p = psutil.Process(pid)
            if p.status() == psutil.STATUS_ZOMBIE:
                try:
                    p.wait(timeout=0)
                    terminated_zombies.add(pid)
                except psutil.TimeoutExpired:
                    pass
        return worker_pids.difference(terminated_zombies)

    def run(self):
        jobs_dict = defaultdict(list)
        for job_instance in self.job_instances:
            # interval can't be smaller than 1s
            assert (isinstance(job_instance.interval, int))
            # interval can't be smaller than 1
            assert (job_instance.interval >= 1)
            jobs_dict[job_instance.interval].append(job_instance)
        max_interval = max(jobs_dict.keys())
        sleep_count = 0
        worker_pids = set()
        init = perf_counter()
        while True:
            try:
                time.sleep(1 - ((perf_counter() - init) % 1))
                worker_pids = self._reap_pids(worker_pids)
                sleep_count += 1
                for interval, jobs in jobs_dict.items():
                    # spawn all jobs that match the current interval
                    if sleep_count % interval == 0:
                        for job in jobs:
                            worker_pids.add(self.job_spawner(job))
                # reset the sleep counter (to infinity!)
                if sleep_count > 0 and sleep_count % max_interval == 0:
                    sleep_count = 0
            except KeyboardInterrupt:
                self._reap_pids(worker_pids)
                break

    def run_once(self, **kwargs):
        pids = list()
        for job_instance in self.job_instances:
            pids.append(self.job_spawner(job_instance, **kwargs))
        for pid in pids:
            os.waitpid(pid, 0)


if __name__ == '__main__':
    scheduler = JobScheduler()
    scheduler.run()
