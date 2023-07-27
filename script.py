import os
import requests
import json
from dotenv import load_dotenv


def get_frames_and_layers(figma_file_key, personal_access_token, page_id):
    url = f"https://api.figma.com/v1/files/{figma_file_key}"
    headers = {"X-Figma-Token": personal_access_token}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            page = data['document']['children'][page_id]
            all_frames = []
            for child in page['children']:
                if child['type'] == 'FRAME':
                    all_frames.append(child)

            if all_frames:
                for frame_id, frame in enumerate(all_frames):
                    frame_data = {
                        'frame_id': frame_id,
                        'name': frame['name'],
                        'attributes': get_frame_layers(frame),
                    }

                    if not os.path.exists('metadata'):
                        os.makedirs('metadata')
                    # Dump the frames_data to a JSON file
                    output_filename = f"frame_{frame_id}.json"
                    file_path = os.path.join('metadata', output_filename)
                    with open(file_path, 'w') as f:
                        json.dump(frame_data, f, indent=2)

                    print(
                        f"Data for frames {frame_id} on Page {page_id} dumped to {output_filename}.")
            else:
                print("No frames found on the specified page.")
        except IndexError:
            print("Error: Page not found in the Figma file.")
    else:
        print("Error:", response.status_code)
        print(response.json())


def get_frame_layers(node):
    if (node['type'] == 'COMPONENT' or node['type'] == 'INSTANCE') and get_component_property_names(node) not in ["No Attribute", "No Expression", "No Accessory", "No ears"]:
        if node['name'].startswith(('0.', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            node['name'] = node['name'].split('.', 1)[1].strip()
        return [{"trait_type": node['name'], "value": get_component_property_names(node)}]
    elif node['type'] == 'FRAME':
        layers = []
        if 'children' in node:
            for child in node['children']:
                layers.extend(get_frame_layers(child))
        return layers
        # return []
    else:
        return []


def get_component_property_names(node):
    properties = ""
    if 'componentProperties' in node:
        component_property = node['componentProperties']
        values = component_property.values()
        properties = list(values)[0].get('value')
        if properties.startswith(('0.', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
            properties = properties.split('.', 1)[1].strip()

    return properties


if __name__ == "__main__":
    load_dotenv()
    figma_file_key = os.getenv("FIGMA_FILE_KEY")
    personal_access_token = os.getenv("FIGMA_API_KEY")
    page_id = 3

    get_frames_and_layers(figma_file_key, personal_access_token, page_id)
