import base64
import json
import os
import stat
import requests

class Vault:
    def __init__(self):
        self.uri = "http://localhost:5157/api/Vault"

    def find_files_by_item_codes(self, item_codes):
        find_components_uri = f"{self.uri}/findcomponents"
        try:
            saved_file_paths = []
            headers = {'Content-Type': 'application/json'}
            
            # Build component → original item lookup (preserves all fields)
            # Use component name as key since multiple components can share the same itemcode
            # (e.g., jacket nozzles N16 and N15 use same part but different positions)
            # Handle both 'comp' (what generation_service sends) and 'component' (what vault API might return)
            item_lookup_by_comp = {}
            item_lookup_by_code = {}
            for item in item_codes:
                comp_name = item.get("comp") or item.get("component", "")
                if comp_name:
                    item_lookup_by_comp[comp_name.lower()] = item
                itemcode = item.get("itemcode", "")
                if itemcode:
                    item_lookup_by_code[itemcode] = item

            response = requests.post(find_components_uri, json={"items": item_codes}, headers=headers)

            if response.status_code != 200:
                print("Failed to retrieve components:", response.text)
                return False

            result = response.json()

            for idx, item in enumerate(result):
                initial_path = item.get("filepath")
                parts = initial_path.split(os.sep)
                # Insert "Vault" before "Designs"
                new_parts = []
                for part in parts:
                    if part == "Designs":
                        new_parts.append("Vault")
                    new_parts.append(part)

                # Join back the path
                path = os.sep.join(new_parts)
                base64_content = item.get("base64")
                component = item.get("component")
                itemcode = item.get("itemcode")

                if not path or not base64_content:
                    print("Missing filepath or content for item:", item)
                    continue

                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                content = base64.b64decode(base64_content)
                os.chmod(path, stat.S_IWRITE)
                with open(path, "wb") as f:
                    os.chmod(path, 0o666)
                    f.write(content)


                # Get original item data to preserve additional fields
                # Try component name first (handles same itemcode for different components)
                # Fall back to itemcode lookup
                comp_key = (component or "").lower()
                original_item = item_lookup_by_comp.get(comp_key, {})
                if not original_item:
                    original_item = item_lookup_by_code.get(itemcode, {})

                saved_file_paths.append({
                    'id': idx + 1,
                    'component': component,
                    'itemcode': itemcode,
                    'filepath': path,
                    'subcomponents': original_item.get("sub_components"),
                    # Preserve nozzle metadata for dynamic handling
                    'fastener_count': original_item.get("fastener_count"),
                    'nozzle_size': original_item.get("nozzle_size"),
                    'nozzle_degree': original_item.get("nozzle_degree"),
                    'nozzle_location': original_item.get("nozzle_location"),
                    'gasket_offset': original_item.get("gasket_offset"),
                })

            return saved_file_paths

        except Exception as e:
            print("Error while connecting to vault:", e)
            return False

    # def find_files_by_item_codes(self, item_codes):
    #     # codes = [item['itemcode'] for item in item_codes]
    #     find_components_uri = f"{self.uri}/findcomponents"
    #     try:
    #         saved_file_paths = []
    #         response = requests.post(find_components_uri, json={"items" : item_codes}, headers = {'Content-Type': 'application/json'})
    #         result = response.json()
    #         for item in result:
    #             path = item["filepath"]
    #             if not os.path.exists(path):
    #                 content = base64.b64decode(item["base64"])

    #                 os.makedirs(os.path.dirname(path), exist_ok=True)
    #                 with open(path, "wb") as f:
    #                     f.write(content)
    #             saved_file_paths.append({'component': item['component'], 'itemcode': item['itemcode'], 'filepath': item['filepath']})
            
    #         # ---------------------------------------------------------------------------------------------------------------
    #         # with requests.post(find_files_uri,  json=new_bom_details, headers = {'Content-Type': 'application/json'}) as r:
    #         #     r.raise_for_status()
    #         #     print(r)
    #             # downloaded_file_name = self.get_file_name_from_response(r)
    #             # if downloaded_file_name :
    #             #     with open(downloaded_file_name, 'wb') as f:
    #             #         for chunk in r.iter_content(chunk_size=8192):
    #             #             if chunk:  # Filter out keep-alive chunks
    #             #                 f.write(chunk)
    #             # return downloaded_file_name
    #         return saved_file_paths
    #     except Exception as e:
    #         print("Error while connecting vault.", e)
    #         return False