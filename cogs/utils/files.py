import os

folder_path = os.getcwd()


def get_initial_extensions():
    extensions_list = []
    for extension in os.listdir(f'{folder_path}/cogs/'):
        if extension.endswith('.py'):
            name = extension[:-3]
            extensions_list.append(f'cogs.{name}')
    return extensions_list
