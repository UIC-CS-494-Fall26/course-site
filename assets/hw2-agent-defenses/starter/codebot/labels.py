"""Part III: labels and the lattice.

A label answers the two questions from lecture:
- confidentiality: may anyone learn this data? (public) Or only a few? (secret)
- integrity: did only trusted parties shape this data? (trusted) Or anyone? (untrusted)

The four labels form a lattice. The bottom is (public, trusted). The top is (secret, untrusted).
"""
from dataclasses import dataclass


# @dataclass writes __init__ and == for us, so Label(secret=True) works and
# two labels with the same fields compare equal. frozen=True makes a label
# read-only after creation.
@dataclass(frozen=True)
class Label:
    """A security label: one field for confidentiality and one for integrity.

    secret=True marks data that only a few may learn, such as the key in .env.
    untrusted=True marks data that an outsider may have shaped, such as an
    issue report or a web page.
    """
    secret: bool = False
    untrusted: bool = False

    def __str__(self):
        """Format the label as a pair, such as "(secret, trusted)"."""
        first = "secret" if self.secret else "public"
        second = "untrusted" if self.untrusted else "trusted"
        return f"({first}, {second})"


PUBLIC_TRUSTED = Label(secret=False, untrusted=False)    # the bottom
SECRET_TRUSTED = Label(secret=True, untrusted=False)
PUBLIC_UNTRUSTED = Label(secret=False, untrusted=True)
SECRET_UNTRUSTED = Label(secret=True, untrusted=True)    # the top


def join(a: Label, b: Label) -> Label:
    """Return the least restrictive label at least as restrictive as both a and b.

    The harness calls join() to combine data. For example, a context that
    has read both the key in .env and an issue report carries the join of
    their two labels.

    TODO (Part III): replace the line below.
    """
    raise NotImplementedError("Part III: implement join() in codebot/labels.py")


def flows_to(a: Label, b: Label) -> bool:
    """Return True when data labeled a may flow into a place labeled b.

    Data may move up the lattice, to an equal or a more restrictive label.
    For example, public data may go into a secret place, and trusted data
    may go into an untrusted place.

    TODO (Part III): replace the line below.
    """
    raise NotImplementedError("Part III: implement flows_to() in codebot/labels.py")
