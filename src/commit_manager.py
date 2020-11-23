# Install: $ pip install gitpython
from git import Repo
import re
from .configs.gerrit_config import *
from .constants import *


def has_multiple_parents(commit):
    return len(commit.parents) > 1


def has_direct_push_permission(committer, permissions):
    # TODO: Check the user permission using two files:
    #   - CONFIG_PROJECT
    #   - CONFIG_GROUP

    return True


# Check if the commit has the first review unit in a chain
def is_first_review(review_units):
    # TODO:
    return True


# Extrcact all review units in a commit
def get_review_units(commit):
    # TODO:
    return []


# Check if the commit has a review unit
def has_review_units(commit):
    return bool(re.search(f"score .*\n.*\n{PGP_START}\n", commit.message))


# Extract PR's commits in a REBASE
def get_rebase_commits(repo, parents):
    merge_commits = []

    #TODO:
    # Get commits until we find the first review unit in the chain
    # Then, keep adding commits until we find a commit that
    # either has a review unit or has multiple parents

    return merge_commits


# Extract PR's commits in a MERGE
def get_merge_commits(repo, parents):
    merge_commits = []

    # Get common ancestor of two parents
    common_ancestor = repo.merge_base(parents[0], parents[1])[0]

    # Get commits between the head of PR and CA
    merge_commit_ids = repo.git.rev_list(
        '--ancestry-path',
        f'{common_ancestor.hexsha}..{parents[1].hexsha}'
        ).split()

    for id in merge_commit_ids:
        merge_commits.append(repo.commit(id))

    return merge_commits


# Extract the GitHub merge requests' commits
def github_extract_merge_request_commits(repo, commit):
    parents = commit.parents

    # Check for FIRSTCOMMIT in the repository
    if not parents:
        return [FIRSTCOMMIT, []]

    if len(parents) == 1:
        # Extract the review units embeded in the Commit
        review_units = get_review_units(commit)

        # Commits with one parent and no review units are DIRECTPUSH
        if not review_units:
            return [DIRECTPUSH, [commit]]

        # Commits with one parent and at least one review unit
        # are either REBASE or SQUASH
        else:
            if len(review_units) == 1:
                if not is_first_review(review_units):
                    return [REBASE, get_rebase_commits(repo, parents)]
                #else
                    #FIXME: differentiate between REBASE and SQUASH

            # Commits with one parent and more than one review unit
            # are SQUASH
            else:
               return [SQUASH, [commit]]

    # Commits with two parents are MERGE
    return [MERGE, get_merge_commits(repo, parents)]


# Extract the Gerrit merge requests' commits
def gerrit_extract_merge_request_commits(commit, permissions):
    parents = commit.parents

    if not parents:
        return []
    else:
        committer = commit.committer
        if (
            not has_review_units(commit)
            and not has_direct_push_permission(committer, permissions)
        ):
            return 'A suspicious commit is found!'
        else:
            if len(parents) == 1:
                return [commit]
            else:
                return [commit, parents[1]]
