"""White-box hunt: extract C from a form, S from a handler, then diff them.

  python3 scripts/whitebox.py --model <name> \
      --form   targets/src/kanboard/app/Template/user_invite/signup.php \
      --handler targets/src/kanboard/app/Controller/UserInviteController.php \
      --helper  targets/src/kanboard/app/Model/UserModel.php

The script runs the three lab prompts in order and prints each table. Read every
row against the code before you trust it, then confirm a gap with replay.py.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _llm import ask  # noqa: E402

PROMPTS = pathlib.Path(__file__).parent.parent / "prompts"


def load(path):
    return pathlib.Path(path).read_text(errors="replace")


def section(title):
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--form", required=True, help="the form template or page")
    ap.add_argument("--handler", required=True, help="the server handler")
    ap.add_argument("--helper", action="append", default=[],
                    help="a helper, model, or middleware the handler calls (repeatable)")
    a = ap.parse_args()

    system = "You are a careful security analyst. Cite file:line for every row. Invent nothing."

    client_code = f"FORM FILE: {a.form}\n\n{load(a.form)}"
    c = ask(a.model, system, load(PROMPTS / "extract-client.md") + "\n\n" + client_code)
    section("C: client constraints")
    print(c)

    server_src = [f"HANDLER FILE: {a.handler}\n\n{load(a.handler)}"]
    for h in a.helper:
        server_src.append(f"HELPER FILE: {h}\n\n{load(h)}")
    s = ask(a.model, system, load(PROMPTS / "extract-server.md") + "\n\n" + "\n\n".join(server_src))
    section("S: server constraints")
    print(s)

    diff = ask(a.model, system,
               load(PROMPTS / "diff.md") + f"\n\nC:\n{c}\n\nS:\n{s}")
    section("Gaps (confirm each with replay.py)")
    print(diff)


if __name__ == "__main__":
    main()
