#!/usr/bin/env python

# Copyright 2015 Earth Sciences Department, BSC-CNS

# This file is part of Autosubmit.

# Autosubmit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Autosubmit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Autosubmit.  If not, see <http://www.gnu.org/licenses/>.
import textwrap


class Status:
    """
    Class to handle the status of a job
    """
    WAITING = 0
    READY = 1
    SUBMITTED = 2
    QUEUING = 3
    RUNNING = 4
    COMPLETED = 5
    FAILED = -1
    UNKNOWN = -2
    SUSPENDED = -3

    def retval(self, value):
        return getattr(self, value)


# noinspection PyPep8
class StatisticsSnippet:
    """
    Class to handle the statistics snippet of a job. It contains header and tailer for
    local and remote jobs
    """

    AS_HEADER = textwrap.dedent("""\

            ###################
            # Autosubmit header
            ###################

            job_name_ptrn='%CURRENT_LOGDIR%/%JOBNAME%'
            echo $(date +%s) > ${job_name_ptrn}_STAT
            rm -f ${job_name_ptrn}_COMPLETED

            ###################
            # Autosubmit job
            ###################

            """)

    # noinspection PyPep8
    AS_TAILER = textwrap.dedent("""\

            ###################
            # Autosubmit tailer
            ###################

            echo $(date +%s) >> ${job_name_ptrn}_STAT
            touch ${job_name_ptrn}_COMPLETED
            exit 0
            """)

