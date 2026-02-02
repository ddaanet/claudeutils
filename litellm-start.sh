#!/usr/bin/env bash
# Start LiteLLM proxy with API keys from env file

set -euo pipefail

# Load all LiteLLM provider keys from env file
# Note: All keys used by proxy come from ~/.config/litellm/env
# This is separate from ~/.claude/ keys used for direct provider access
if [[ ! -f ~/.config/litellm/env ]]; then
    echo "Error: ~/.config/litellm/env not found" >&2
    echo "Copy ~/.config/litellm/env.example and add your keys" >&2
    exit 1
fi

set -a
source ~/.config/litellm/env
set +a

# Start LiteLLM proxy
exec litellm --config ~/.config/litellm/config.yaml --port 4000
