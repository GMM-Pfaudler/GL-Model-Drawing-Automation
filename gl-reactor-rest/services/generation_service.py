import json
import os
import re
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
    

    # def flatten_components(self, data):
    #     flat_list = []

    #     for comp_dict in data:
    #         for comp_key, comp_val in comp_dict.items():
    #             # Extract model info
    #             model_info = comp_val.get('model_info', {})
    #             itemcode = model_info.get('itemCode', '')
    #             drawingnumber = model_info.get('drawingNumber', '')

    #             # Add main component
    #             flat_list.append({
    #                 'comp': comp_key.lower(),
    #                 'drawingnumber': drawingnumber,
    #                 'member': '',
    #                 'itemcode': f"7005{model_info.get('model', '').replace('CE_', 'CE0')}-000" if model_info.get('model') else itemcode,
    #                 'sub_components': []
    #             })

    #             # Process all nozzles dynamically
    #             for k, v in comp_val.items():
    #                 if k.startswith('nozzle_'):
    #                     try:
    #                         nozzle_data = json.loads(v)
    #                     except Exception:
    #                         continue

    #                     nozzle_no = nozzle_data.get('nozzleNo', '')
    #                     size = nozzle_data.get('size', '')
    #                     degree = nozzle_data.get('degree', '')
    #                     fittings = nozzle_data.get('fittings', [])

    #                     # Loop through fittings
    #                     for fitting in fittings:
    #                         fname_raw = fitting.get('name', '')
    #                         # Convert spaces, special chars → underscore
    #                         fname = re.sub(r'\s+', '_', fname_raw.strip().lower())

    #                         fitemcode = fitting.get('itemCode', '')
    #                         fdrawing = fitting.get('drawingNumber', '')

    #                         # Skip if degree is '-' or empty
    #                         if degree in ('', '-', None):
    #                             comp_name = f"{nozzle_no}_{size}_{fname}"
    #                         else:
    #                             comp_name = f"{nozzle_no}_{size}_{degree}_{fname}"

    #                         flat_list.append({
    #                             'comp': comp_name.lower(),
    #                             'drawingnumber': fdrawing,
    #                             'member': '',
    #                             'itemcode': fitemcode,
    #                             'sub_components': []
    #                         })
    #     return flat_list

    def flatten_components(self, data):
        flat_list = []

        def normalize_name(name):
            """Normalize component or fitting names: lowercase + underscores for spaces/special chars."""
            return re.sub(r'[^a-zA-Z0-9]+', '_', name.strip().lower()).strip('_')

        for comp_dict in data:
            component_name = next(iter(comp_dict))
            if component_name == 'monoblock':
                'monoblock'
                for comp_key, comp_val in comp_dict.items():
                    # Normalize top-level component name
                    comp_name = normalize_name(comp_key)

                    # Extract model info
                    model_info = comp_val.get('model_info', {})
                    itemcode = model_info.get('itemCode', '')
                    drawingnumber = model_info.get('drawingNumber', '')
                    model = model_info.get('model', '')

                    # Add main component
                    flat_list.append({
                        'comp': comp_name,
                        'partnumber': drawingnumber,
                        'member': '',
                        'itemcode': itemcode,
                        'sub_components': []
                    })

                    # Process all nozzles
                    for k, v in comp_val.items():
                        if k.startswith('nozzle_'):
                            try:
                                nozzle_data = json.loads(v)
                            except Exception:
                                continue

                            nozzle_no = nozzle_data.get('nozzleNo', '')
                            size = nozzle_data.get('size', '')
                            degree = nozzle_data.get('degree', '')
                            fittings = nozzle_data.get('fittings', [])

                            for fitting in fittings:
                                fname_raw = fitting.get('name', '')
                                fname = normalize_name(fname_raw)
                                fitemcode = fitting.get('itemCode', '')
                                fdrawing = fitting.get('drawingNumber', '')

                                # Skip if degree is '-' or empty
                                if degree in ('', '-', None):
                                    comp_name_full = f"{nozzle_no}_{size}_{fname}"
                                else:
                                    comp_name_full = f"{nozzle_no}_{size}_{degree}_{fname}"

                                flat_list.append({
                                    'comp': normalize_name(comp_name_full),
                                    'partnumber': fdrawing,
                                    'member': '',
                                    'itemcode': fitemcode,
                                    'sub_components': []
                                })

            if component_name == 'jacket':
                'jacket'
                jacket_data = comp_dict['jacket']
                comp_name = jacket_data.get('component', 'Unknown')

                # Jacket itself
                if 'jacket' in jacket_data:
                    j = jacket_data['jacket']
                    flat_list.append({
                        'comp': normalize_name(comp_name),
                        'partnumber': j.get('drawingNumberJacket', ''),
                        'member': '',
                        'itemcode': j.get('itemCodeJacket', ''),
                        'sub_components': []
                    })

                # Support
                if 'support' in jacket_data:
                    s = jacket_data['support']
                    flat_list.append({
                        'comp': normalize_name(s.get('component', 'Support')),
                        'partnumber': s.get('drawingNumberJacketSupport', ''),
                        'member': '',
                        'itemcode': s.get('itemCodeJacketSupport', ''),
                        'sub_components': []
                    })

                # Earthing
                if 'earthing' in jacket_data:
                    e = jacket_data['earthing']
                    flat_list.append({
                        'comp': normalize_name('Earthing'),
                        'partnumber': e.get('drawingNumberJacketEarthing', ''),
                        'member': '',
                        'itemcode': e.get('itemCodeJacketEarthing', ''),
                        'sub_components': []
                    })

                # Nozzles (list)
                if 'nozzles' in jacket_data:
                    for n in jacket_data['nozzles']:
                        flat_list.append({
                            'comp': normalize_name(f"{component_name} Nozzle {n.get('nozzle', '')}"),
                            'partnumber': n.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': n.get('itemCode', ''),
                            'sub_components': []
                        })

            if component_name == 'sensor':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)

                # Iterate through subcomponents
                for sub_key, sub_data in data.items():
                    if sub_key in ['component', 'model_info']:
                        continue  # skip metadata
                    
                    if isinstance(sub_data, dict):
                        model_info = sub_data.get('model_info', {})
                        flat_list.append({
                            'comp': normalize_name(f"{comp_name}  {sub_key.capitalize()}"),
                            'partnumber': model_info.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': model_info.get('itemCode', ''),
                            'sub_components': []
                        })

            if component_name == 'driveAssembly':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)

                # Iterate through subcomponents
                for sub_key, sub_data in data.items():
                    if sub_key in ['component', 'model_info']:
                        continue  # skip metadata

                    if isinstance(sub_data, dict):
                        # Try to find drawingNumber and itemCode (the keys can vary slightly)
                        drawing_number = next((v for k, v in sub_data.items() if 'drawingNumber' in k), None)
                        item_code = next((v for k, v in sub_data.items() if 'itemCode' in k), None)

                        flat_list.append({
                            'comp': normalize_name(f"{comp_name} {sub_key}"),
                            'partnumber': drawing_number or '',
                            'member': '',
                            'itemcode': item_code or '',
                            'sub_components': []
                        })
            
            if component_name == 'airVentCouplingPlug':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = key[0].upper() + key[1:]  # capitalize nicely

                # Handle nozzle list
                if 'nozzles' in data:
                    for nozzle in data['nozzles']:
                        flat_list.append({
                            'comp': normalize_name(f"{comp_name} {nozzle.get('nozzle', '')}"),
                            'partnumber': nozzle.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': nozzle.get('itemCode', ''),
                            'sub_components': []
                        })
            
            if comp_name == 'insulation':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)

                # Iterate through all potential subcomponents
                for sub_key, sub_data in data.items():
                    if sub_key in ['component', 'model_info', 'insulationReq', 'insulationType']:
                        continue  # skip metadata

                    if isinstance(sub_data, dict):
                        # Find the drawing number and item code
                        drawing_number = next((v for k, v in sub_data.items() if 'drawingNumber' in k), None)
                        item_code = next((v for k, v in sub_data.items() if 'itemCode' in k), None)

                        flat_list.append({
                            'comp': normalize_name(f"{comp_name} {sub_key[0].upper() + sub_key[1:]}"),
                            'partnumber': drawing_number or '',
                            'member': '',
                            'itemcode': item_code or '',
                            'sub_components': []
                        })

            if component_name == 'namePlateBracket' or component_name == 'driveHood' or component_name == 'diaphragmRing' or component_name =='springBalanceAssembly' or component_name =='MHCClamp' or component_name =='coc' or component_name =='bfCClamp' or component_name == 'agitator' or component_name == 'shaftclosure' or component_name == 'gearbox' or component_name == 'motor':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)
                model_info = data.get('model_info', {})

                flat_list.append({
                    'comp': normalize_name(comp_name),
                    'partnumber': model_info.get('drawingNumber', ''),
                    'member': '',
                    'itemcode': model_info.get('itemCode', ''),
                    'sub_components': []
                })
            
        return flat_list

    def generate_model(self, model_details):
        components = self.get_component_list(model_details=model_details)
        # component_item_codes = self.flatten_components(data=components)
        # print(component_item_codes)
        # # result = self.process_components(data=components)
        # all_item_codes = []
        # for obj in components:
        #     all_item_codes.extend(self.extract_item_codes(obj))
        # print(all_item_codes)
        # item_codes = self.get_item_codes(components_details=components)
        # item_codes = ['7005CE06300-000', '5625-0015', '3616-0003', '5605B-0016']
        component_item_codes = [{'id':1, 'comp': 'monoblock', 'partnumber': '', 'member': '','itemcode':'7005CE06300-000', 'sub_components': []}, # done 
                                {'id':2, 'comp': 'jacket', 'partnumber': '', 'member': '', 'itemcode':'5625-0015', 'sub_components': []}, # done
                                {'id':3, 'comp': 'diapharmring', 'partnumber': '', 'member': '', 'itemcode':'3616-0003', 'sub_components': []}, # done
                                {'id':4, 'comp': 'sidebracket', 'partnumber': '', 'member': '', 'itemcode':'5605B-0016', 'sub_components': []}, # done
                                {'id':5, 'comp': 'earthing_boss', 'partnumber': '', 'member': '', 'itemcode':'3627-0009', 'sub_components': []}, # done
                                {'id':6, 'comp': 'jacketnozzle_shell', 'partnumber': '', 'member': '', 'itemcode':'5621-1035', 'sub_components': []}, # done
                                {'id':7, 'comp': 'jacketnozzle_bottom', 'partnumber': '', 'member': '', 'itemcode':'5621-1036', 'sub_components': []}, # done
                                {'id':8, 'comp': 'ms_coupling', 'partnumber': '', 'member': 'SA105_COUPLING_50L_96-GPF-7236-17834 R3.iam', 'itemcode':'', 'sub_components': []}, #5617NS0028 # air-vent
                                {'id':9, 'comp': 'baffle_plate', 'partnumber': '', 'member': '', 'itemcode':'3502B0099', 'sub_components': []}, # add to jacket nozzle

                                # Manhole
                                {'id':10, 'comp': 'manhole_gasket_1', 'partnumber': '', 'member': '', 'itemcode':'T1-0086', 'sub_components': []},
                                {'id':11, 'comp': 'bush_type_protection_ring', 'partnumber': '', 'member': '', 'itemcode':'T5B0579', 'sub_components': []},
                                {'id':12, 'comp': 'manhole_gasket_2', 'partnumber': '', 'member': '', 'itemcode':'T1-0086', 'sub_components': []},
                                {'id':13, 'comp': 'manhole_cover', 'partnumber': '', 'member': '', 'itemcode':'7053-0115', 'sub_components': []},
                                {'id':14, 'comp': 'manhole_c_clamp', 'partnumber': '', 'member': '', 'itemcode':'79010136', 'sub_components': []}, # done
                                {'id':15, 'comp': 'spring_balance_assembly', 'partnumber': '', 'member': '90-GPF-5403 R1_SPRING BALANCE ASSLY WITH WASHER_500NB_FAST.iam', 'itemcode':'', 'sub_components': []}, #56181000-0101 done
                                
                                {'id':16, 'comp': 'manhole_sight_glass_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0362', 'sub_components': []},
                                {'id':17, 'comp': 'manhole_sight_glass', 'partnumber': '', 'member': '', 'itemcode':'760039', 'sub_components': []},
                                {'id':18, 'comp': 'manhole_sight_flange', 'partnumber': '', 'member': '', 'itemcode':'5602-0092', 'sub_components': []},
                                
                                {'id':19, 'comp': 'manhole_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0151', 'sub_components': []},
                                {'id':20, 'comp': 'manhole_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS2366', 'sub_components': []},

                                # COC
                                {'id':21, 'comp': 'coc_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0104', 'sub_components': []}, # add
                                {'id':22, 'comp': 'coc', 'partnumber': '', 'member': '', 'itemcode':'7004-0002', 'sub_components': []}, # done
                                {'id':23, 'comp': 'coc_c_clamp', 'partnumber': '', 'member': '', 'itemcode':'79010013', 'sub_components': []}, # body flange c-clamp
                                {'id':24, 'comp': 'center_nozzle_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0365', 'sub_components': []}, # m nozzle
                                {'id':25, 'comp': 'drive_assembly', 'partnumber': '', 'member': 'HD100M-60-160-015-DM-0007_RATIO_14_CGL_IE3_GL.iam', 'itemcode':'', 'sub_components': []},
                                {'id':26, 'comp': 'mechanical_seal', 'partnumber': '', 'member': '', 'itemcode':'80061824', 'sub_components': []}, # done shaftclousure

                                {'id':27, 'comp': 'mechanical_seal_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0013', 'sub_components': []},
                                {'id':28, 'comp': 'mechanical_seal_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0237', 'sub_components': []},

                                {'id':29, 'comp': 'agitator', 'partnumber': '', 'member': '', 'itemcode':'9015-0019', 'sub_components': []}, # done
                                
                                # N2 nozzle 
                                {'id':30, 'comp': 'n2_150_60_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'id':31, 'comp': 'n2_150_60_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'id':32, 'comp': 'n2_150_60_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                {'id':33, 'comp': 'n2_150_60_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'id':34, 'comp': 'n2_150_60_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'id':35, 'comp': 'n2_150_60_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                # N3 nozzle
                                {'id':36, 'comp': 'n3_150_95_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'id':37, 'comp': 'n3_150_95_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'id':38, 'comp': 'n3_150_95_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},
                                
                                {'id':39, 'comp': 'n3_150_95_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'id':40, 'comp': 'n3_150_95_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'id':41, 'comp': 'n3_150_95_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                # N5 nozzle
                                {'id':42, 'comp': 'n5_250_135_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0354', 'sub_components': []},
                                {'id':43, 'comp': 'n5_250_135_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0366', 'sub_components': []},
                                {'id':44, 'comp': 'n5_250_135_baffle', 'partnumber': '', 'member': '', 'itemcode':'901601-0033', 'sub_components': []},

                                {'id':45, 'comp': 'n5_250_135_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0072', 'sub_components': []},
                                {'id':46, 'comp': 'n5_250_135_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'id':47, 'comp': 'n5_250_135_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                # N6 nozzle
                                {'id':48, 'comp': 'n6_150_180_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0352', 'sub_components': []},
                                {'id':49, 'comp': 'n6_150_180_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'id':50, 'comp': 'n6_150_180_toughenedglass', 'partnumber': '', 'member': '', 'itemcode':'760031', 'sub_components': []},
                                {'id':51, 'comp': 'n6_150_180_lightglass', 'partnumber': '', 'member': '', 'itemcode':'5602-0094', 'sub_components': []},
                                {'id':52, 'comp': 'n6_150_180_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0072', 'sub_components': []},
                                {'id':53, 'comp': 'n6_150_180_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'id':54, 'comp': 'n6_150_180_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},

                                {'id':55, 'comp': 'n7_250_225_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0361', 'sub_components': []},
                                {'id':56, 'comp': 'n7_250_225_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0366', 'sub_components': []},
                                {'id':57, 'comp': 'n7_250_225_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0021', 'sub_components': []},

                                {'id':58, 'comp': 'n7_250_225_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS2298', 'sub_components': []},
                                {'id':59, 'comp': 'n7_250_225_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0156', 'sub_components': []},
                                {'id':60, 'comp': 'n7_250_225_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0008', 'sub_components': []},

                                # N9 nozzle
                                {'id':61, 'comp': 'n9_150_265_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'id':62, 'comp': 'n9_150_265_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'id':63, 'comp': 'n9_150_265_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                {'id':64, 'comp': 'n9_150_265_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'id':65, 'comp': 'n9_150_265_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'id':66, 'comp': 'n9_150_265_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},
                                
                                # N10 nozzle
                                {'id':67, 'comp': 'n10_150_300_split_flange', 'partnumber': '', 'member': '', 'itemcode':'5619-0360', 'sub_components': []},
                                {'id':68, 'comp': 'n10_150_300_gasket', 'partnumber': '', 'member': '', 'itemcode':'T1-0364', 'sub_components': []},
                                {'id':69, 'comp': 'n10_150_300_blind_cover', 'partnumber': '', 'member': '', 'itemcode':'7058-0019', 'sub_components': []},

                                {'id':70, 'comp': 'n10_150_300_fastener', 'partnumber': '', 'member': '', 'itemcode':'13CS0069', 'sub_components': []},
                                {'id':71, 'comp': 'n10_150_300_washer', 'partnumber': '', 'member': '', 'itemcode':'13WS0155', 'sub_components': []},
                                {'id':72, 'comp': 'n10_150_300_nut', 'partnumber': '', 'member': '', 'itemcode':'13CSNT-0007', 'sub_components': []},
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