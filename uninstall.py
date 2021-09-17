import winreg as reg
def delete_reg_key(root_key,key,menu_name):
    try:
        parent_key = reg.OpenKey(root_key,key)
    except Exception as msg:
        print(msg)
        return
    if parent_key:
        try:
            menu_key = reg.OpenKey(parent_key,menu_name)
        except Exception as msg:
            print(msg)
            return
        if menu_key:
            try:
                reg.DeleteKey(menu_key,'command')
            except Exception as msg:
                print(msg)
                return
            else:
                reg.DeleteKey(parent_key,menu_name)


if __name__ == '__main__':
    menu_name = 'post file'
    delete_reg_key(reg.HKEY_CLASSES_ROOT, r'Directory\\shell', menu_name)
    delete_reg_key(reg.HKEY_CLASSES_ROOT, r'Directory\\Background\\shell', menu_name)
    delete_reg_key(reg.HKEY_CLASSES_ROOT, r'Drive\\shell', menu_name)
