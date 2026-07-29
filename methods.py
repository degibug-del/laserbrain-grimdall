"""methods.py — phronesis's own workflows, as stored methods.

lasergear is the instructions layer, so this is where the methods live. Running it writes
them into the store (laserstore), where anything — nova, a future session, Diego — can vend
them.

WHY THESE THREE

Not invented. Each is a method that was performed BY HAND on 2026-07-28/29 and got wrong,
in a way a declared workflow would have caught:

  release   0.12.0 went to PyPI with 53 exports instead of 56. The wheel was built before
            workflow.py existed and never rebuilt. PyPI versions cannot be reused.
  deploy    a commit and a push went out on a RED build, because the steps were written as
            separate shell lines instead of chained — so a failure did not stop what
            followed.
  grammar   the 1.8.0/1.9.0 sync into phronesis-world was uncommitted when git filter-repo
            hard-reset the working tree, and two copies silently reverted to 1.7.0.

Every one of those is an ordering failure, which is the failure a workflow exists to make
impossible: a step that must precede another, and did not.

WHAT A STORED METHOD IS AND IS NOT

It carries the steps, the goal each step is for, and which of them cannot be taken back. It
carries NO code. The point is not automation — these are not scripts. The point is that the
shape is written down and measurable, so a run can be checked against the method rather
than against someone's memory of it.

`irreversible` and `outward` are not decoration. A step marked either way is refused by the
Operator unless a person authorized it, per action and per session, so `pypi-upload` cannot
be reached by an agent working unattended.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / 'Library/Mobile Documents/com~apple~CloudDocs/'
                       'phronesis/laserbrain-sdk'))

from laserbrain import Store, Workflow          # noqa: E402


def release() -> Workflow:
    """Publish a laserbrain version to PyPI.

    The rebuild step is FIRST and separate from the build check on purpose. 0.12.0's whole
    failure was a stale artifact passing a check that only ever looked at symbols someone
    had listed by hand.
    """
    w = Workflow(goal='publish a verified laserbrain release to PyPI')
    w.step('test', goal='every test file exits zero')
    w.step('bump', goal='the version rises in pyproject and __init__')
    w.step('edit-changelog', goal='the changelog records what changed and why')
    w.step('build-wheel', goal='rebuild the wheel from the current tree')
    w.step('verify-artifact',
           goal='the built wheel exports match the tree and the headline path runs')
    w.step('commit', goal='the source of this release is committed and pushed')
    w.step('upload-pypi', goal='upload the release to PyPI',
           irreversible=True, outward=True)
    w.step('verify-published',
           goal='install from PyPI in a clean venv outside the tree and import')
    # Added 2026-07-29 after this method was USED. Bumping the SDK invalidates the drift
    # vectors in phronesis-world, which are generated from it — so the site's laserstore
    # gate fails on the next build, in a different repo, with nothing linking the two.
    # A release is not finished when PyPI has the wheel; it is finished when everything
    # generated FROM the wheel agrees with it again.
    w.step('generate-vectors',
           goal='regenerate the drift vectors so the site gate compares against this version')
    return w


def deploy() -> Workflow:
    """Ship phronesis.world.

    `gate-check` is its own step rather than part of the build because that is precisely
    the distinction that was lost: a red build did not stop the commit that followed it.

    `deploy` is irreversible. It was written reversible=False here first, and the dictionary
    linter caught it on its first run against a real method — putting a build in front of
    users cannot be un-shown, and a later deploy replaces it rather than undoing it.
    """
    w = Workflow(goal='ship phronesis.world with every gate green')
    w.step('build', goal='the site builds and every prebuild gate passes')
    w.step('gate-check', goal='no gate reports a problem')
    w.step('commit', goal='the source of this deploy is committed and pushed')
    w.step('deploy', goal='publish the built site to Cloudflare Pages',
           irreversible=True, outward=True)
    w.step('verify-live',
           goal='fetch the changed page from the deployment URL, not the cached domain')
    return w


def grammar_bump() -> Workflow:
    """Change the canonical grammar.

    `commit-copies` exists because of the specific way this failed: the synced copies were
    left uncommitted and a history rewrite discarded them. A generated file that is not
    committed is not synced, it is only currently correct.
    """
    w = Workflow(goal='change the canonical grammar and keep every copy honest')
    w.step('edit-canonical', goal='edit lasermind grammar.json, the one source')
    w.step('bump-version', goal='raise laserbrain_grammar so the change has a name')
    w.step('generate-hash',
           goal='recompute content_hash over the file including its trailing newline')
    w.step('gate', goal='check-grammar-version agrees the hash describes the content')
    w.step('sync', goal='propagate the canonical file to every copy')
    w.step('commit-copies',
           goal='commit the synced copies so a rewrite cannot silently revert them')
    return w


METHODS = {'release': release, 'deploy': deploy, 'grammar-bump': grammar_bump}


def main():
    store = Store()
    for name, build in METHODS.items():
        w = build()
        path = store.put(w, name)
        acts = [s.name for s in w.steps if s.irreversible or s.outward]
        print(f'  stored {name:<13} {len(w.steps)} steps, gated: {acts or "none"}')
        print(f'         {path}')
    print()
    print('  catalogue:')
    for row in store.catalogue():
        print(f'    {row["name"]:<13} {row["goal"]}')


if __name__ == '__main__':
    main()
