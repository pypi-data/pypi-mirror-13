# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import itertools

import pytest

import thutils


@pytest.fixture
def subproc_wrapper():
    return thutils.subprocwrapper.SubprocessWrapper()


DEVICE = "eth0"

RATE_LIST = [
    "",
    "--rate 100K",
    "--rate 0.5M",
    "--rate 0.1G",
]
DELAY_LIST = [
    "",
    "--delay 0",
    "--delay 10",
    "--delay 100",
]
LOSS_LIST = [
    "",
    "--loss 0",
    "--loss 0.1",
    "--loss 1",
]
OVERWRITE_LIST = [
    "",
    "--overwrite",
]


class Test_tcconfig:

    @pytest.mark.parametrize(["rate", "delay", "loss", "overwrite"], [
        opt_list
        for opt_list in itertools.product(
            RATE_LIST, DELAY_LIST, LOSS_LIST, OVERWRITE_LIST)
    ])
    def test_smoke(self, subproc_wrapper, rate, delay, loss, overwrite):
        option_list = [rate, delay, loss, overwrite]
        command = "tcset --device eth0 " + " ".join(option_list)
        assert subproc_wrapper.run(command) == 0

        command = "tcdel --device eth0"
        assert subproc_wrapper.run(command) == 0
