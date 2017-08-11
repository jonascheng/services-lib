from unittest import TestCase

import pytest

from soocii_services_lib.util import wait_for_internet_connection


class WaitForItTestCase(TestCase):
    @pytest.mark.timeout(60)
    def test_wait_for_google(self):
        wait_for_internet_connection('www.google.com', 80)
