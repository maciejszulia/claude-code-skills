# ADR 0004: Gitea as the third push URL

## Status

Accepted (commit `16d9987`).

## Context

Every repository has GitHub as the main remote and GitLab as a mirror. A local Gitea is added as a third copy. A test showed that an error of the second push URL stops `git push` before the third URL.

## Decision

`gitea_mirror.py` appends the Gitea URL as the last push URL of each clone, after GitHub and GitLab, and never touches the fetch URL. `--apply` creates a missing Gitea repository with the GitHub visibility, pushes every branch and tag to Gitea only, without force, and sets the GitHub default branch. `--compare` checks the hash of the default branch. The token is read from a file and sent only in an HTTP header.

## Consequences

- A Gitea outage cannot stop the GitLab mirror.
- A GitLab error still stops the push to Gitea.
- After the Gitea push the script fetches the remote, because git moves the remote-tracking refs to the Gitea state.

## Evidence

- Docstring of `tools/gitea-middle-remote/gitea_mirror.py` (pair decision P10).
- Commits `16d9987`, `1bbea4c`, `9be1016`.
