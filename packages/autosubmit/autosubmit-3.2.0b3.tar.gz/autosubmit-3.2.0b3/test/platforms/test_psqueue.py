import unittest
import autosubmit.platforms.localplatform
from time import sleep


class PlatformsTests(unittest.TestCase):
    def setUp(self):
        # have to create the cmd file in the tmp folder before testing
        self.queue = PsQueue('l000')
        self.scriptname = "l000_19960101_fc0_1_init.cmd"

    def tearDown(self):
        pass

    def testMethod(self):
        self.queue.check_remote_log_dir()
        j = self.queue.send_script(self.scriptname)
        print(j)
        job_id = self.queue.submit_job(self.scriptname)
        print(job_id)
        self.assertNotEqual(job_id, 0)
        status = self.queue.check_job(job_id, 0)
        self.assertNotEqual(status, 1)
        sleep(60)
        status = self.queue.check_job(job_id, 0)
        print self.queue.check_job(job_id, 0)
        self.assertNotEqual(status, 0)
        self.queue.cancel_job(job_id)
        status = self.queue.check_job(job_id, 0)
        self.assertNotEqual(status, 0)


if __name__ == '__main__':
    unittest.main()
