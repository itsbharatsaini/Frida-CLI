def config_list() -> None:
    """"""
    print("Config list")


def configurate_api_keys() -> None:
    """"""
    print("Configurating")


def exec_config(list: bool) -> None:
    """"""
    if list:
        config_list()
    else:
        configurate_api_keys()
