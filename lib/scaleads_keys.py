import os, stat

CRED_DIR = os.path.expanduser("~/.scale-ads")
CRED_FILE = os.path.join(CRED_DIR, "credentials.env")


def load():
    keys = {}
    if os.path.exists(CRED_FILE):
        for line in open(CRED_FILE):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                keys[k.strip()] = v.strip()
    return keys


def save(new_keys: dict):
    keys = load()
    keys.update(new_keys)
    os.makedirs(CRED_DIR, exist_ok=True)
    with open(CRED_FILE, "w") as f:
        for k, v in keys.items():
            f.write(f"{k}={v}\n")
    os.chmod(CRED_FILE, stat.S_IRUSR | stat.S_IWUSR)


def mask(value: str) -> str:
    return f"{value[:4]}…{value[-4:]}" if len(value) > 8 else "set"


if __name__ == "__main__":
    keys = load()
    print(f"Credentials file: {CRED_FILE}  ({'exists' if os.path.exists(CRED_FILE) else 'missing'})")
    for k, v in keys.items():
        print(f"  {k:<22} {mask(v)}")
