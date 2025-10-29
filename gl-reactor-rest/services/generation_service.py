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

    # def process_fittings(self, fittings):
    #     """Convert fittings into structured list of dicts."""
    #     sub_fittings = []
    #     for fit in fittings:
    #         sub_fittings.append({
    #             'comp': fit.get('fittingNo', ''),
    #             'partnumber': '',
    #             'member': '',
    #             'itemcode': fit.get('itemCode', ''),
    #             'drawingNumber': fit.get('drawingNumber', ''),
    #             'sub_components': []
    #         })
    #     return sub_fittings

    # def process_nozzles(self, comp_data):
    #     """Convert all nozzles (and fittings inside them) into proper structure."""
    #     nozzles_list = []
    #     for key, val in comp_data.items():
    #         if key.startswith("nozzle_"):
    #             try:
    #                 nozzle_data = json.loads(val)
    #                 fittings = nozzle_data.get('fittings', [])
    #                 nozzle_data['fittings'] = self.process_fittings(fittings)
                    
    #                 nozzles_list.append({
    #                     'comp': nozzle_data.get('nozzleNo', ''),
    #                     'partnumber': '',
    #                     'member': '',
    #                     'itemcode': nozzle_data.get('itemCode', ''),
    #                     'drawingNumber': nozzle_data.get('drawingNumber', ''),
    #                     'sub_components': nozzle_data['fittings']
    #                 })
    #             except json.JSONDecodeError:
    #                 continue
    #     return nozzles_list

    # def process_component(self, comp_name, comp_data):
    #     """Process each component based on its type."""
    #     model_info = comp_data.get('model_info', {})
        
    #     # Base structure
    #     comp_dict = {
    #         'comp': comp_name.lower(),
    #         'partnumber': '',
    #         'member': '',
    #         'itemcode': model_info.get('itemCode', ''),
    #         'drawingNumber': model_info.get('drawingNumber', ''),
    #         'sub_components': []
    #     }

    #     # Custom logic per component
    #     if comp_name.lower() == 'monoblock':
    #         comp_dict['sub_components'] = self.process_nozzles(comp_data)
        
    #     elif comp_name.lower() == 'coc':
    #         # Future logic for coc, if it ever has subcomponents
    #         comp_dict['sub_components'] = []

    #     return comp_dict

    # def process_components(self, data):
    #     """Main processor for all components."""
    #     result = []
    #     for comp_dict in data:
    #         for comp_name, comp_data in comp_dict.items():
    #             result.append(self.process_component(comp_name, comp_data))
    #     return result    
    
    def generate_model(self, model_details):
        # components = self.get_component_list(model_details=model_details)
        # # result = self.process_components(data=components)
        # all_item_codes = []
        # for obj in components:
        #     all_item_codes.extend(self.extract_item_codes(obj))
        # print(all_item_codes)
        # item_codes = self.get_item_codes(components_details=components)
        # item_codes = ['7005CE06300-000', '5625-0015', '3616-0003', '5605B-0016']
        component_item_codes = [{'comp': 'monoblock', 'partnumber': '', 'member': '','itemcode':'7005CE06300-000', 'sub_components': []}, 
                                {'comp': 'jacket', 'partnumber': '', 'member': '', 'itemcode':'5625-0015', 'sub_components': []}, 
                                {'comp': 'diapharmring', 'partnumber': '', 'member': '', 'itemcode':'3616-0003', 'sub_components': []}, 
                                {'comp': 'sidebracket', 'partnumber': '', 'member': '', 'itemcode':'5605B-0016', 'sub_components': []}, 
                                {'comp': 'jacketnozzle_shell', 'partnumber': '', 'member': '', 'itemcode':'5621-1035', 'sub_components': []}, 
                                {'comp': 'jacketnozzle_bottom', 'partnumber': '', 'member': '', 'itemcode':'5621-1036', 'sub_components': []},
                                {'comp': 'ms_coupling', 'partnumber': '', 'member': 'SA105_COUPLING_50L_96-GPF-7236-17834 R3.iam', 'itemcode':'', 'sub_components': []}, #5617NS0028
                                {'comp': 'baffle_plate', 'partnumber': '', 'member': '', 'itemcode':'3502B0099', 'sub_components': []},

                                # Manhole
                                {'comp': 'manhole_gasket_1', 'partnumber': '', 'member': '', 'itemcode':'T1-0086', 'sub_components': []},
                                {'comp': 'bush_type_protection_ring', 'partnumber': '', 'member': '', 'itemcode':'T5B0579', 'sub_components': []},
                                {'comp': 'manhole_gasket_2', 'partnumber': '', 'member': '', 'itemcode':'T1-0086', 'sub_components': []},
                                {'comp': 'manhole_cover', 'partnumber': '', 'member': '', 'itemcode':'7053-0115', 'sub_components': []},
                                {'comp': 'manhole_c_clamp', 'partnumber': '', 'member': '', 'itemcode':'79010136', 'sub_components': []},
                                {'comp': 'spring_balance_assembly', 'partnumber': '', 'member': '90-GPF-5403 R1_SPRING BALANCE ASSLY WITH WASHER_500NB_FAST.iam', 'itemcode':'', 'sub_components': []}, #56181000-0101
                                {'comp': 'manhole_sight_glass_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0362', 'sub_components': []},
                                {'comp': 'manhole_sight_glass', 'partnumber': '', 'member': '', 'itemcode':'760039', 'sub_components': []},
                                {'comp': 'manhole_sight_flange', 'partnumber': '', 'member': '', 'itemcode':'5602-0092', 'sub_components': []},
                                
                                {'comp': 'manhole_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'comp': 'manhole_washer', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'comp': 'manhole_nut', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                # COC
                                {'comp': 'coc_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0104', 'sub_components': []},
                                {'comp': 'coc', 'partnumber': '', 'member': '', 'itemcode':'7004-0002', 'sub_components': []},
                                {'comp': 'coc_c_clamp', 'partnumber': '', 'member': '', 'itemcode':'79010013', 'sub_components': []},
                                {'comp': 'center_nozzle_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0365', 'sub_components': []},
                                {'comp': 'drive_assembly', 'partnumber': '', 'member': 'HD100M-60-160-015-DM-0007_RATIO_14_CGL_IE3_GL.iam', 'itemcode':'', 'sub_components': []},
                                {'comp': 'mechanical_seal', 'partnumber': '', 'member': '', 'itemcode':'80061824', 'sub_components': []},
                                {'comp': 'agitator', 'partnumber': '', 'member': '', 'itemcode':'9015-0019', 'sub_components': []},
                                
                                # N2 nozzle
                                {'comp': 'n2_150_60_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'comp': 'n2_150_60_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'comp': 'n2_150_60_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                {'comp': 'n2_150_60_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'comp': 'n2_150_60_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'comp': 'n2_150_60_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                # N3 nozzle
                                {'comp': 'n3_150_95_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'comp': 'n3_150_95_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'comp': 'n3_150_95_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},
                                
                                {'comp': 'n3_150_95_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'comp': 'n3_150_95_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'comp': 'n3_150_95_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                # N5 nozzle
                                {'comp': 'n5_250_135_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0354', 'sub_components': []},
                                {'comp': 'n5_250_135_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0366', 'sub_components': []},
                                {'comp': 'n5_250_135_baffle', 'partnumber': '', 'member': '', 'itemcode':'901601-0033', 'sub_components': []},

                                # N6 nozzle
                                {'comp': 'n6_150_180_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0352', 'sub_components': []},
                                {'comp': 'n6_150_180_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'comp': 'n6_150_180_toughenedglass', 'partnumber': '', 'member': '', 'itemcode':'760031', 'sub_components': []},
                                {'comp': 'n6_150_180_lightglass', 'partnumber': '', 'member': '', 'itemcode':'5602-0094', 'sub_components': []},
                                {'comp': 'n6_150_180_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0072', 'sub_components': []},
                                {'comp': 'n6_150_180_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'comp': 'n6_150_180_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                {'comp': 'n7_250_225_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0361', 'sub_components': []},
                                {'comp': 'n7_250_225_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0366', 'sub_components': []},
                                {'comp': 'n7_250_225_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0021', 'sub_components': []},

                                {'comp': 'n7_250_225_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS2298', 'sub_components': []},
                                {'comp': 'n7_250_225_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0156', 'sub_components': []},
                                {'comp': 'n7_250_225_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0008', 'sub_components': []},

                                # N9 nozzle
                                {'comp': 'n9_150_265_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'comp': 'n9_150_265_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'comp': 'n9_150_265_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                {'comp': 'n9_150_265_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'comp': 'n9_150_265_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'comp': 'n9_150_265_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},
                                
                                # N10 nozzle
                                {'comp': 'n10_150_300_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'comp': 'n10_150_300_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'comp': 'n10_150_300_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                {'comp': 'n10_150_300_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'comp': 'n10_150_300_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'comp': 'n10_150_300_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},
                                ]
        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=component_item_codes)
        res = self.inventor.generate(components=downloaded_components_files, model_details=model_details)
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
    


    # {'comp': 'n1_500_0', 'partnumber': '', 'member': '', 'itemcode':'', 'sub_components': [
    #     {'comp': 'n1_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n1_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n1_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n1_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},
    # {'comp': 'n2_150_60', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n2_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
    #     {'comp': 'n2_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
    #     {'comp': 'n2_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},
    #     {'comp': 'n2_other', 'partnumber': '', 'member': '', 'itemcode':'', 'sub_components': []},
    # ]},
    # {'comp': 'n3_150_95', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n3_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n3_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n3_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n3_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},
    # {'comp': 'n5_250_135', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n5_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n5_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n5_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n5_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},
    # {'comp': 'n6_150_180', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n6_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n6_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n6_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n6_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},
    # {'comp': 'n7_250_225', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n7_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n7_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n7_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n7_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},
    # {'comp': 'n9_150_265', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n9_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n9_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n9_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n9_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},
    # {'comp': 'n10_150_300', 'partnumber': '', 'member': '', 'itemcode':'', 
    #     'sub_components': [
    #     {'comp': 'n10_split_flange', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n10_gasket', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n10_blind_cover', 'partnumber': '', 'member': '', 'itemcode':''},
    #     {'comp': 'n10_other', 'partnumber': '', 'member': '', 'itemcode':''},
    # ]},