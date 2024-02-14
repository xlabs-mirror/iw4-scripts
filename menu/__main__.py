import re
import xml.etree.ElementTree as ET

def parse_item_def(item_def_str):
    item_def = {}
    for line in item_def_str.split('\n'):
        key, value = re.match(r'(\w+)\s+(\w+)', line).groups()
        if key == 'name':
            item_def['name'] = value
        elif key == 'rect':
            item_def['rect'] = list(map(int, re.findall(r'\d+', value)))
        elif key == 'visible':
            item_def['visible'] = (value == '1')
        elif key == 'decoration':
            item_def['decoration'] = (value == '1')
        elif key == 'style':
            item_def['style'] = (value == '3')
        elif key == 'forecolor':
            item_def['forecolor'] = list(map(int, re.findall(r'\d+', value)))
        elif key == 'background':
            item_def['background'] = value
        elif key == 'textscale':
            item_def['textscale'] = float(value)
        # Add more cases for other keys if needed
    return item_def

# The entire content of the file
file_content = ''

with open(r"G:\CoD 6 (Dump)\ui_mp\main_text.menu", "r", encoding="utf-8") as f:
    file_content = f.read()

# Regular expression pattern to match the relevant sections
pattern = re.compile(r'menuDef\s+\{([\s\S]*?)\}', re.MULTILINE)

menu_defs = re.findall(pattern, file_content)

menus = {}

# Iterate through the menuDefs and extract the required information
for menu_def in menu_defs:
    menus[menu_def] = []
    # item_defs = menu_def.findall('.//itemDef')
    item_defs = re.findall(r'itemDef\s+\{([\s\S]+?)\s+\}', menu_def, re.MULTILINE)
    for item_def_str in item_defs:
        item_def = parse_item_def(item_def_str)
        menus[menu_def].append(item_def)

for menu in menus:
    print(menu)
    for item in menus[menu]:
        print(f"\t{item}")