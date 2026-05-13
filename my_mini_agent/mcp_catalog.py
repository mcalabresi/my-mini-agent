mcp_servers = {
    "imageMCP": {
        "command": "npx",
        "args": [
            "mcp-remote",
            "https://api.imgmcp.com/mcp",
            "--header",
            "Authorization: Bearer ${IMAGEMCP_API_KEY}",
        ],
        "env": {"IMAGEMCP_API_KEY": "PUT_YOUR_API_KEY_IN_DOT_ENV_FILE"},
    },
    "pixserp": {
        "command": "npx",
        "args": [
            "-y",
            "mcp-remote",
            "https://pixserp.com/api/v1/mcp",
            "--header",
            "Authorization: Bearer ${PIXSERP_API_KEY}",
        ],
        "env": {"PIXSERP_API_KEY": "PUT_YOUR_API_KEY_IN_DOT_ENV_FILE"},
    },
}
