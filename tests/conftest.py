from dataclasses import dataclass

import json

from typing import Union

from pathlib import Path

import pytest

from bitcoin_client.ledger_bitcoin import TransportClient, Client, Chain, createClient

from speculos.client import SpeculosClient

import os
import re

import random

random.seed(0)  # make sure tests are repeatable

# path with tests
conftest_folder_path: Path = Path(__file__).parent


ASSIGNMENT_RE = re.compile(r'^\s*([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*(.*)$', re.MULTILINE)


def get_app_version() -> str:
    makefile_path = conftest_folder_path.parent / "Makefile"
    if not makefile_path.is_file():
        raise FileNotFoundError(f"Can't find file: '{makefile_path}'")

    makefile: str = makefile_path.read_text()

    assignments = {
        identifier: value for identifier, value in ASSIGNMENT_RE.findall(makefile)
    }

    return f"{assignments['APPVERSION_M']}.{assignments['APPVERSION_N']}.{assignments['APPVERSION_P']}"


def pytest_addoption(parser):
    parser.addoption("--hid", action="store_true")
    parser.addoption("--headless", action="store_true")
    parser.addoption("--enableslowtests", action="store_true")


@pytest.fixture(scope="module")
def sw_h_path():
    # sw.h should be in src/boilerplate/sw.h
    sw_h_path = conftest_folder_path.parent / "src" / "boilerplate" / "sw.h"

    if not sw_h_path.is_file():
        raise FileNotFoundError(f"Can't find sw.h: '{sw_h_path}'")

    return sw_h_path


@pytest.fixture(scope="module")
def app_version() -> str:
    return get_app_version()


@pytest.fixture
def hid(pytestconfig):
    return pytestconfig.getoption("hid")


@pytest.fixture
def headless(pytestconfig):
    return pytestconfig.getoption("headless")


@pytest.fixture
def enable_slow_tests(pytestconfig):
    return pytestconfig.getoption("enableslowtests")


@pytest.fixture
def comm(request, hid, app_version: str) -> Union[TransportClient, SpeculosClient]:
    if hid:
        client = TransportClient("hid")
    else:
        # We set the app's name before running speculos in order to emulate the expected
        # behavior of the SDK's GET_VERSION default APDU.
        # The app name is 'Bitcoin' or 'Bitcoin Test' for mainnet/testnet respectively.
        # We leave the speculos default 'app' to avoid relying on that value in tests.
        os.environ['SPECULOS_APPNAME'] = f'app:{app_version}'
        client = SpeculosClient(
            str(conftest_folder_path.parent.joinpath("bin/app.elf")),
            ['--sdk', '2.1']
        )
        client.start()

        try:
            automation_file = conftest_folder_path.joinpath(request.function.automation_file)
        except AttributeError:
            automation_file = None

        if automation_file:
            rules = json.load(open(automation_file))
            client.set_automation_rules(rules)

    yield client

    client.stop()


@pytest.fixture
def is_speculos(comm: Union[TransportClient, SpeculosClient]) -> bool:
    return isinstance(comm, SpeculosClient)


@pytest.fixture
def client(comm: Union[TransportClient, SpeculosClient]) -> Client:
    return createClient(comm, chain=Chain.TEST, debug=True)


@dataclass(frozen=True)
class SpeculosGlobals:
    seed = "glory promote mansion idle axis finger extra february uncover one trip resource lawn turtle enact monster seven myth punch hobby comfort wild raise skin"
    # TODO: those are for testnet; we could compute them for any network from the seed
    master_extended_privkey = "xprvA1oScBuhBjyAXhwqT1bVroVHGwFWgjEThWzeAQEMzNUdWcfmJ1Wk7B3g6PL32xifvo6dkVpp3E5ysTvMk2HDj1ALK85iXAYKfvtFCHhUbBA"
    master_extended_pubkey = "xpub6Eno1hSb27XTkC2JZ38WDwS1py616BxK4jvExndyYi1cPQzuqYpzeyN9wd9HgDBPTRdPpEBLcFpr2LChwR1gYjeHvJDTrVqCowJfWUwHvdQ"
    master_key_fingerprint = 0xF5ACC2FD
    master_compressed_pubkey = bytes.fromhex(
        "0251ec84e33a3119486461a44240e906ff94bf40cf807b025b1ca43332b80dc9db"
    )
    wallet_registration_key = bytes.fromhex(
        "7463d6d1a82f4647ead048c625ae0c27fe40b6d0d5f2d24104009ae9d3b7963c"
    )


@pytest.fixture
def speculos_globals() -> SpeculosGlobals:
    return SpeculosGlobals()
