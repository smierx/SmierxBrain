import os
import env

def extract_headings_from_markdown(file_path):
    headings = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        for line in lines:
            if line.startswith('#'):
                headings.append(line.strip())

    return headings

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
            content.append(line)

    return content


if __name__ == "__main__":
    config = env.get_config()
    CONFIG_PATH = config["PATHS"]["BASE"] + "/Configs"

    for file in os.listdir(CONFIG_PATH):
        result = ""
        tmp_config = f"{CONFIG_PATH}/{file}"
        headers = extract_headings_from_markdown(tmp_config)
        for h in headers:
            counter = h.count("#")
            file_name = h.split("# ")[1]
            content = find_content_under_heading(config["PATHS"]["BASE"]+"/Zettel/"+file_name+".md", "Inhalt")
            result = result + h + "\n"
            if len(content) > 0:
                for x in content:
                    row_end = "\n" if not x.endswith("\n") else ""
                    result = result + x + row_end

        with open(config["PATHS"]["BASE"]+"/Results/"+file, "w", encoding='utf-8') as file:
            file.write(result)
