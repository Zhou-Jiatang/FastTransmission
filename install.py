import winreg as reg
from os import path


def add_context_menu(menu_name, command, reg_root_key_path, reg_key_path, shortcut_key):

    key = reg.OpenKey(reg_root_key_path, reg_key_path)
    reg.SetValue(key, menu_name, reg.REG_SZ, menu_name + '(&{0})'.format(shortcut_key))

    sub_key = reg.OpenKey(key, menu_name)
    reg.SetValue(sub_key, 'command', reg.REG_SZ, '"' + command + '" "%v"')

    reg.CloseKey(sub_key)
    reg.CloseKey(key)


def add_show_file_path_menu():
    menu_name = 'post file'
    abs_path = path.abspath('./server/simple_http_server.py')

    # py_command = r'python E:\\py_WorkSpace\\FastTransmission\\test.py'
    py_command = r'E:\py_WorkSpace\FastTransmission\dist\main\main.exe'
    add_context_menu(menu_name, py_command, reg.HKEY_CLASSES_ROOT, r'Directory\\shell', 'P')
    add_context_menu(menu_name, py_command, reg.HKEY_CLASSES_ROOT, r'Directory\\Background\\shell', 'P')
    add_context_menu(menu_name, py_command, reg.HKEY_CLASSES_ROOT, r'Drive\\shell', 'P')


if __name__ == '__main__':
    add_show_file_path_menu()
