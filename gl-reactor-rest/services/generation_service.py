import json
import os
from services.vault_service import Vault
from services.inventor_service import Inventor
class Generation:
    def __init__(self):
        self.vault = Vault()
        self.inventor = Inventor()

    def get_component_list(self, model_details):
        keys = list(model_details['details'].keys())
        if len(keys) < 1:
            print("Invalid component_details structure")
            return False
        so_value = model_details['details'][keys[0]]
        folder_name = f"D:\\GL\\SO\\{so_value}"
        file_path = f"{folder_name}\\{so_value}.json"
        # ✅ Load existing data
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    data_list = json.load(file)
                    if not isinstance(data_list, list):
                        raise ValueError("JSON structure must be a list of dicts.")
            except json.JSONDecodeError:
                print("Invalid JSON format, starting with empty list.")
                data_list = []
            except Exception as e:
                print(f"Error reading file: {e}")
                return data_list
        return data_list
    
    def extract_item_codes(self, obj, component=None):
        item_codes = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if 'itemCode' in key:
                    item_entry = {
                        'itemCode': value,
                        'component': component or 'Unknown'
                    }

                    # If this is a nozzle, add the nozzle name
                    if component and component.lower() == 'nozzle' and 'nozzle' in obj:
                        item_entry['nozzle'] = obj['nozzle']

                    item_codes.append(item_entry)

                elif isinstance(value, dict):
                    next_component = value.get('component', component)
                    item_codes.extend(self.extract_item_codes(value, next_component))

                elif isinstance(value, list):
                    # Special case: check if list of nozzles
                    if key == 'nozzles':
                        for nozzle_obj in value:
                            item_codes.extend(self.extract_item_codes(nozzle_obj, 'Nozzle'))
                    else:
                        for item in value:
                            item_codes.extend(self.extract_item_codes(item, component))

        return item_codes

    def get_item_code_by_component(self, components, comp_details):
        keys = list(comp_details['details'].keys())
        if len(keys) < 1:
            print("Invalid component_details structure")
            return False
        comp = comp_details['details'][keys[1]]
        result = [d for d in components if comp in d]
        model_info = result[0][comp].get("model_info", {})
        item_code = model_info.get("itemCode")
        return [item_code]

    def get_item_codes(self, components_details):
        item_codes = []
        for entry in components_details:
            for outer_dict in entry.values():
                model_info = outer_dict.get("model_info", {})
                item_code = model_info.get("itemCode")
                if item_code:
                    item_codes.append(item_code)
        print(item_codes)
        return item_codes
    
    def generate_model(self, model_details):
        components = self.get_component_list(model_details=model_details)
        # all_item_codes = []
        # for obj in components:
        #     all_item_codes.extend(self.extract_item_codes(obj))
        # print(all_item_codes)
        # item_codes = self.get_item_codes(components_details=components)
        # item_codes = ['7005CE06300-000', '5625-0015', '3616-0003', '5605B-0016']
        component_item_codes = [{'comp': 'monoblock', 'partnumber': '', 'member': '','itemcode':'7005CE06300-000'}, 
                                {'comp': 'jacket', 'partnumber': '', 'member': '', 'itemcode':'5625-0015'}, 
                                {'comp': 'diapharmring', 'partnumber': '', 'member': '', 'itemcode':'3616-0003'}, 
                                {'comp': 'sidebracket', 'partnumber': '', 'member': '', 'itemcode':'5605B-0016'}, 
                                {'comp': 'jacketnozzle_shell', 'partnumber': '', 'member': '', 'itemcode':'5621-1035'}, 
                                {'comp': 'jacketnozzle_bottom', 'partnumber': '', 'member': '', 'itemcode':'5621-1036'},
                                {'comp': 'ms_coupling', 'partnumber': '', 'member': 'SA105_COUPLING_50L_96-GPF-7236-17834 R3', 'itemcode':''}, #5617NS0028
                                {'comp': 'baffle_plate', 'partnumber': '', 'member': '', 'itemcode':'3502B0099'},
                                {'comp': 'manhole_gasket_1', 'partnumber': '', 'member': '', 'itemcode':'T1-0086'},
                                {'comp': 'bush_type_protection_ring', 'partnumber': '', 'member': '', 'itemcode':'T5B0579'},
                                {'comp': 'manhole_gasket_2', 'partnumber': '', 'member': '', 'itemcode':'T1-0086'},
                                {'comp': 'manhole_cover', 'partnumber': '', 'member': '', 'itemcode':'7053-0115'}]
                                # {'comp': 'ms_coupling_bottom', 'partnumber': '96-GPF-7236', 'member': 'SA105_COUPLING_50L_96-GPF-7236-17834 R3', 'itemcode':''},
        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=component_item_codes)
        res = self.inventor.generate(components=downloaded_components_files)
        print(res)
        print(downloaded_components_files)
        return "Model Generated"
    
    def open_component(self, compo_details):
        components = self.get_component_list(model_details=compo_details)
        item_code = self.get_item_code_by_component(components=components, comp_details=compo_details)
        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=item_code)
        print(downloaded_components_files)
        result = self.inventor.open(downloaded_components_files)
        return result