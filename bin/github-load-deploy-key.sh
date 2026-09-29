#!/bin/bash -eu
# Load the deploy key into ssh-agent so later steps can push over SSH.
# This replaces webfactory/ssh-agent to avoid handing the key to third-party
# code.
set -o pipefail
mkdir -p ~/.ssh
# Take GitHub's host keys from its API over HTTPS instead of trusting whatever
# ssh-keyscan happens to return. Authenticate with GH_TOKEN, as runners share
# IPs and hit the rate limit for anonymous requests.
gh api meta --jq '.ssh_keys[] | "github.com " + .' >>~/.ssh/known_hosts
# Keep the output in a variable so that set -e catches a failure; eval "$(...)"
# would succeed on empty output.
agent=$(ssh-agent -s -a "$RUNNER_TEMP/ssh-agent.sock")
eval "$agent"
ssh-add - <<<"$SSH_PRIVATE_KEY"
# Later steps run in new shells, so hand the agent socket over to them.
echo "SSH_AUTH_SOCK=$SSH_AUTH_SOCK" >>"$GITHUB_ENV"
