import base64
import json
import os
import requests

class Vault:
    def __init__(self):
        self.uri = "http://localhost:5157/api/Vault"

    def find_files_by_item_codes(self, item_codes):
        # codes = [item['itemcode'] for item in item_codes]
        find_components_uri = f"{self.uri}/findcomponents"
        try:
            saved_file_paths = []
            response = requests.post(find_components_uri, json={"items" : item_codes}, headers = {'Content-Type': 'application/json'})
            result = response.json()
            for item in result:
                path = item["filepath"]
                if not os.path.exists(path):
                    content = base64.b64decode(item["base64"])

                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "wb") as f:
                        f.write(content)
                saved_file_paths.append({'component': item['component'], 'itemcode': item['itemcode'], 'filepath': item['filepath']})
            
            # ---------------------------------------------------------------------------------------------------------------
            # with requests.post(find_files_uri,  json=new_bom_details, headers = {'Content-Type': 'application/json'}) as r:
            #     r.raise_for_status()
            #     print(r)
                # downloaded_file_name = self.get_file_name_from_response(r)
                # if downloaded_file_name :
                #     with open(downloaded_file_name, 'wb') as f:
                #         for chunk in r.iter_content(chunk_size=8192):
                #             if chunk:  # Filter out keep-alive chunks
                #                 f.write(chunk)
                # return downloaded_file_name
            return saved_file_paths
        except Exception as e:
            print("Error while connecting vault.", e)
            return False