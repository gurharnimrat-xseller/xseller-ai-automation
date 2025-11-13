import base64, os, sys, uuid, shutil, subprocess
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "12000"))
HEAVY_TIMEOUT_SEC = int(os.getenv("HEAVY_TIMEOUT_SEC", "90"))
def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)
def should_offload(prompt: str, est_sec: int | None = None) -> bool:
    return _estimate_tokens(prompt) >= MAX_TOKENS or (est_sec or 0) >= HEAVY_TIMEOUT_SEC
def offload_to_gemini(prompt: str, model: str | None = None) -> str:
    rid = str(uuid.uuid4())[:8]
    b64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
    model = model or os.getenv("OFFLOAD_MODEL", "gemini-1.5-pro-latest")
    if shutil.which("gh"):
        cmd = ["gh","workflow","run","offload_gemini.yml","-f",f"prompt_b64={b64}","-f",f"request_id={rid}","-f",f"model={model}"]
        subprocess.run(cmd, check=False)
        print(f"Offloaded to Gemini (request_id={rid}). Exiting locally.")
    else:
        print("Heavy task detected. Run this in your terminal:")
        print(f'gh workflow run offload_gemini.yml -f prompt_b64="{b64}" -f request_id="{rid}" -f model="{model}"')
    return rid
if __name__ == "__main__":
    prompt = sys.stdin.read()
    if should_offload(prompt, None):
        offload_to_gemini(prompt)
        sys.exit(0)
    else:
        print("Not heavy; proceed locally.")
