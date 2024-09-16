import json

import yaml
import os
import time

def find_content_under_heading(file_path, heading):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    content = []
    heading_found = False
    heading_level = None

    for line in lines:
        if line.strip().startswith('#'):
            current_heading_level = len(line) - len(line.lstrip('#'))
            current_heading = line.strip().lstrip('#').strip()

            if current_heading == heading:
                heading_found = True
                heading_level = current_heading_level
                continue

            if heading_found and current_heading_level <= heading_level:
                break

        if heading_found:
            content.append(line.split("- [[")[1].split("]]")[0])

    return content


def read_metadata_from_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if lines[0].strip() == '---':
        yaml_block = []
        for line in lines[1:]:
            if line.strip() == '---':
                break
            yaml_block.append(line)

        # Metadaten aus dem YAML-Block extrahieren
        metadata = yaml.safe_load(''.join(yaml_block))
        return metadata
    else:
        return {}


def extract_parent_name(parent_str):
    if parent_str:
        return parent_str.strip('[]')
    return None


def sort_children(node):
    if node.get("children"):
        sorted_children = dict(sorted(node["children"].items(), key=lambda item: item[1]["order"]))
        node["children"] = sorted_children
        for child in node["children"].values():
            sort_children(child)


def build_nested_structure(data):
    nodes = {item['name']: item for item in data}  # Erstelle ein Dictionary mit den Knoten nach Name
    tree = {}

    for item in data:
        name = item['name']
        parent = item['parent']

        if parent is None:
            tree[name] = nodes[name]
        else:
            parent_node = nodes[parent]
            if "children" not in parent_node or parent_node["children"] == {}:
                parent_node["children"] = {}
            parent_node["children"][name] = nodes[name]


    for root_node in tree.values():
        sort_children(root_node)

    return tree


def build_tree(directory):
    unsorted_data = []
    for file in os.listdir(directory):
        tmp_metadata = read_metadata_from_markdown(os.path.join(directory, file))
        parent = extract_parent_name(tmp_metadata.get('parent', None))
        order = tmp_metadata.get('order')
        tmp_data = {
            "name": file.split(".md")[0],
            "order":order,
            "children": {},
            "parent": parent
        }
        unsorted_data.append(tmp_data)

    nested_tree = build_nested_structure(unsorted_data)


    return nested_tree

def flatten_structure(node, depth=0):
    flat_list = []

    flat_list.append(f"{'#' * (depth + 1)} {node['name']}")

    if "children" in node and node["children"]:
        sorted_children = sorted(node["children"].values(), key=lambda x: x["order"])
        for child in sorted_children:
            flat_list.extend(flatten_structure(child, depth + 1))

    return flat_list

def create_flat_list_for_roots(nested_data, root_names):
    flat_list = []

    for root_name in root_names:
        if root_name in nested_data:
            root_node = nested_data[root_name]
            flat_list.extend(flatten_structure(root_node))

    return flat_list



if __name__ == "__main__":
    BASE_PATH: str = ""#TODO in env
    directory = BASE_PATH+"/Zettel/"
    for x in os.listdir(BASE_PATH+"/MoC"):
        tmp_moc = x.split(".md")[0]
        example = find_content_under_heading(BASE_PATH+"/MoC/"+tmp_moc+".md","Inhaltsverzeichnis")
        nested_data = build_tree(directory)

        flat_list = create_flat_list_for_roots(nested_data,example)

        name = tmp_moc

        if os.path.exists(BASE_PATH + "/Configs/"+tmp_moc+".md"):
            tmp_metadata = read_metadata_from_markdown(BASE_PATH + "/Configs/"+tmp_moc+".md")
            if not tmp_metadata.get("rewrite"):
                name = "TestMoc" + str(int(time.time()))

        with open(BASE_PATH + "/Configs/"+name+".md", "w") as file:
            file.write("---\n")
            file.write("rewrite: true\n")
            file.write("---\n")
            for line in flat_list:
                file.write(line)
                file.write("\n")
