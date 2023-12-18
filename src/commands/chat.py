def load_path(path: str):
    """"""
    print(f"path: {path}")


def exec_chat(path: str | None, tokens: bool):
    """"""
    print("Chat")
    if path:
        load_path(path)
    if tokens:
        print(f"tokens: {tokens}")
