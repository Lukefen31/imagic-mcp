"""Send initialize, tools/list and a tools/call over stdio; print a summary."""
import json, subprocess, sys

cmd = sys.argv[1:] or [sys.executable, "server.py"]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

def rpc(msg):
    p.stdin.write(json.dumps(msg) + "\n"); p.stdin.flush()
    if "id" in msg:
        return json.loads(p.stdout.readline())

init = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-03-26", "capabilities": {},
    "clientInfo": {"name": "check", "version": "0"}}})
print("initialize:", init["result"]["serverInfo"], init["result"]["protocolVersion"])
rpc({"jsonrpc": "2.0", "method": "notifications/initialized"})
tl = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
tools = tl["result"]["tools"]
print("tools/list:", len(tools), "tools:", ", ".join(t["name"] for t in tools))
call = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "list_presets", "arguments": {}}})
r = call["result"]
print("tools/call isError:", r.get("isError"), "|", r["content"][0]["text"][:90])
p.stdin.close(); p.wait(timeout=10)
assert len(tools) > 0 and r.get("isError") is True
print("OK")
