"""Public tests for HW2. They use the scripted model, so no API key is needed.

    python3 -m unittest tests.test_public -v

The tests start the two local servers when the servers are not already running.
"""
import contextlib
import io
import shutil
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path

from codebot import agent, labels

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = sorted((ROOT / "attacks" / "samples").glob("*.md"))
ALL_LABELS = [labels.PUBLIC_TRUSTED, labels.SECRET_TRUSTED,
              labels.PUBLIC_UNTRUSTED, labels.SECRET_UNTRUSTED]

server_process = None  # the server process that setUpModule started, if any


def port_open(port):
    """Return True when some server accepts connections on 127.0.0.1:port."""
    with socket.socket() as s:
        # connect_ex() returns 0 on success and an error number otherwise.
        return s.connect_ex(("127.0.0.1", port)) == 0


# unittest calls setUpModule() once before the first test, and
# tearDownModule() once after the last test.
def setUpModule():
    """Start the two servers when the docs port is free, and wait up to five seconds for them."""
    global server_process
    if port_open(9766):
        return
    # subprocess.Popen starts a program and returns at once, without waiting.
    server_process = subprocess.Popen([sys.executable, str(ROOT / "servers" / "servers.py")],
                                      stdout=subprocess.DEVNULL)
    for _ in range(50):
        if port_open(9766):
            break
        time.sleep(0.1)


def tearDownModule():
    """Stop the servers, if setUpModule started them."""
    if server_process:
        server_process.terminate()
        server_process.wait()


def run(*args):
    """Run the agent with these command-line arguments, hide its output, and return the outcome dict."""
    # redirect_stdout sends every print() inside the with-block into a string buffer.
    with contextlib.redirect_stdout(io.StringIO()):
        return agent.main(list(args))


def safe(result):
    """Return True when a run leaked nothing and left settings.json unchanged."""
    return not result["leak"] and not result["corrupted"]


def have_sandbox():
    """Return True when this machine has sandbox-exec (macOS) or the docker command."""
    # shutil.which() finds a program on the PATH, or returns None.
    return shutil.which("sandbox-exec") is not None or shutil.which("docker") is not None


# Inside a loop, self.subTest() reports each case on its own, so one failing
# case leaves the other cases running.

class Labels(unittest.TestCase):
    """Part III: join() and flows_to() on all four labels."""

    def test_join(self):
        """The join of two labels is secret when either is secret, and untrusted when either is untrusted."""
        for a in ALL_LABELS:
            for b in ALL_LABELS:
                j = labels.join(a, b)
                self.assertEqual(j.secret, a.secret or b.secret)
                self.assertEqual(j.untrusted, a.untrusted or b.untrusted)

    def test_flows_to(self):
        """Data flows up the lattice and to its own label, and nowhere else."""
        self.assertTrue(labels.flows_to(labels.PUBLIC_TRUSTED, labels.SECRET_UNTRUSTED))
        self.assertFalse(labels.flows_to(labels.SECRET_TRUSTED, labels.PUBLIC_UNTRUSTED))
        self.assertFalse(labels.flows_to(labels.PUBLIC_UNTRUSTED, labels.SECRET_TRUSTED))
        for a in ALL_LABELS:
            self.assertTrue(labels.flows_to(a, a))


class Policy(unittest.TestCase):
    """Part II: the per-task policy alone."""

    def test_tasks_still_work(self):
        """Each of T1 to T4 completes under the policy."""
        for task in agent.TASKS:
            with self.subTest(task=task):
                self.assertTrue(run("--task", task, "--defenses", "policy")["task_ok"])

    def test_samples_blocked(self):
        """Each sample attack ends with no leak and no corruption under the policy."""
        for attack in SAMPLES:
            with self.subTest(attack=attack.name):
                self.assertTrue(safe(run("--attack", str(attack), "--defenses", "policy")))


class IFC(unittest.TestCase):
    """Part III: information flow control alone."""

    def test_tasks_still_work(self):
        """Each of T1 to T4 completes under the label rules."""
        for task in agent.TASKS:
            with self.subTest(task=task):
                self.assertTrue(run("--task", task, "--defenses", "ifc")["task_ok"])

    def test_samples_blocked(self):
        """Each sample attack ends with no leak and no corruption under the label rules."""
        for attack in SAMPLES:
            with self.subTest(attack=attack.name):
                self.assertTrue(safe(run("--attack", str(attack), "--defenses", "ifc")))


# skipUnless skips the whole class on a machine with no sandbox.
@unittest.skipUnless(have_sandbox(), "needs sandbox-exec (macOS) or docker")
class Sandbox(unittest.TestCase):
    """Part II: the sandbox alone."""

    def test_tests_still_run(self):
        """T3's unit tests still pass inside the sandbox."""
        self.assertTrue(run("--task", "T3", "--defenses", "sandbox")["task_ok"])

    def test_shell_attack_blocked(self):
        """The shell sample's request to the attacker fails inside the sandbox."""
        attack = str(ROOT / "attacks" / "samples" / "shell_docs.md")
        self.assertTrue(safe(run("--attack", attack, "--defenses", "sandbox")))


class AllDefenses(unittest.TestCase):
    """All the defenses together, with the sandbox when this machine has one."""

    def test_tasks_still_work(self):
        """Each of T1 to T4 completes safely under every defense at once."""
        if have_sandbox():
            defenses = "policy,ifc,sandbox"
        else:
            defenses = "policy,ifc"
        for task in agent.TASKS:
            with self.subTest(task=task):
                result = run("--task", task, "--defenses", defenses)
                self.assertTrue(result["task_ok"] and safe(result))


if __name__ == "__main__":
    unittest.main()
