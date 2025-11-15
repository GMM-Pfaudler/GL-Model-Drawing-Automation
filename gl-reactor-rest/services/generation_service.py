import json
import os
import re
from services.vault_service import Vault
from services.inventor_service import Inventor
from repositories.mongo_db import Mongo
class Generation:
    def __init__(self):
        self.vault = Vault()
        self.inventor = Inventor()
        self.mongo = Mongo(db="testdb")

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

    def flatten_components(self, data):
        id = 0
        flat_list = []
        target_components = {
            'namePlateBracket', 'driveHood', 'diaphragmRing', 'springBalanceAssembly',
            'MHCClamp', 'coc', 'bfCClamp', 'agitator', 'shaftclosure', 'gearbox', 'motor'
        }
        def normalize_name(name):
            """Normalize component or fitting names: lowercase + underscores for spaces/special chars."""
            return re.sub(r'[^a-zA-Z0-9]+', '_', name.strip().lower()).strip('_')

        for comp_dict in data:
            component_name = next(iter(comp_dict))
            if component_name == 'monoblock':
                id = 0
                for comp_key, comp_val in comp_dict.items():
                    # Normalize top-level component name
                    comp_name = normalize_name(comp_key)

                    # Extract model info
                    model_info = comp_val.get('model_info', {})
                    itemcode = model_info.get('itemCode', '')
                    drawingnumber = model_info.get('drawingNumber', '')
                    model = model_info.get('model', '')

                    id += 1
                    # Add main component
                    flat_list.append({
                        'id': id,
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
                            fasteners = nozzle_data.get('Fastner', [])  # ✅ handle fasteners too

                            # Combine fittings + fasteners
                            all_subs = fittings + fasteners

                            for fitting in all_subs:
                                fname_raw = fitting.get('name', '')
                                fname = normalize_name(fname_raw)
                                fitemcode = fitting.get('itemCode', '')
                                fdrawing = fitting.get('drawingNumber', '')

                                # Construct component name
                                if degree in ('', '-', None):
                                    comp_name_full = f"{nozzle_no}_{size}_{fname}"
                                else:
                                    comp_name_full = f"{nozzle_no}_{size}_{degree}_{fname}"

                                fitting_comp = normalize_name(comp_name_full)

                                id += 1
                                flat_list.append({
                                    'id': id,
                                    'comp': fitting_comp,
                                    'partnumber': fdrawing,
                                    'member': '',
                                    'itemcode': fitemcode,
                                    'sub_components': []
                                })


            if component_name == 'jacket':
                
                jacket_data = comp_dict['jacket']
                comp_name = jacket_data.get('component', 'Unknown')

                # Jacket itself
                if 'jacket' in jacket_data:
                    id = id + 1
                    j = jacket_data['jacket']
                    flat_list.append({
                        'id': id,
                        'comp': normalize_name(comp_name),
                        'partnumber': j.get('drawingNumberJacket', ''),
                        'member': '',
                        'itemcode': j.get('itemCodeJacket', ''),
                        'sub_components': []
                    })

                # Support
                if 'support' in jacket_data:
                    id = id + 1
                    s = jacket_data['support']
                    flat_list.append({
                        'id': id,
                        'comp': normalize_name(s.get('component', 'Support')),
                        'partnumber': s.get('drawingNumberJacketSupport', ''),
                        'member': '',
                        'itemcode': s.get('itemCodeJacketSupport', ''),
                        'sub_components': []
                    })

                # Earthing
                if 'earthing' in jacket_data:
                    id = id + 1
                    e = jacket_data['earthing']
                    flat_list.append({
                        'id': id,
                        'comp': normalize_name('Earthing'),
                        'partnumber': e.get('drawingNumberJacketEarthing', ''),
                        'member': '',
                        'itemcode': e.get('itemCodeJacketEarthing', ''),
                        'sub_components': []
                    })

                # Nozzles (list)
                if 'nozzles' in jacket_data:
                    for n in jacket_data['nozzles']:
                        id = id + 1
                        flat_list.append({
                            'id': id,
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
                        id = id + 1
                        model_info = sub_data.get('model_info', {})
                        flat_list.append({
                            'id': id,
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
                        id = id + 1
                        flat_list.append({
                            'id': id,
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
                        id = id + 1
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{comp_name} {nozzle.get('nozzle', '')}"),
                            'partnumber': nozzle.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': nozzle.get('itemCode', ''),
                            'sub_components': []
                        })
            
            if component_name == 'insulation':
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
                        id = id + 1
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{comp_name} {sub_key[0].upper() + sub_key[1:]}"),
                            'partnumber': drawing_number or '',
                            'member': '',
                            'itemcode': item_code or '',
                            'sub_components': []
                        })

            if component_name in target_components:
                key, data = next(iter(comp_dict.items()))
                
                comp_name = data.get('component', key)
                model_info = data.get('model_info', {})

                'namePlateBracket', 'driveHood', 'diaphragmRing', 'springBalanceAssembly',
                'MHCClamp', 'coc', 'bfCClamp', 'agitator', 'shaftclosure', 'gearbox', 'motor'
                id = id + 1
                flat_list.append({
                    'id': id,
                    'comp': normalize_name(comp_name),
                    'partnumber': model_info.get('drawingNumber', ''),
                    'member': '',
                    'itemcode': model_info.get('itemCode', ''),
                    'sub_components': []
                })
            
        return flat_list

    def build_standard_model(self, data):
        """Build standardized model structure from list of component dicts."""

        # Initialize base structure
        standard_model = {
            "reactor": "",
            "model": "",
            "standard": "NON-GMP",
            "model_info": {
                "glass": "",
                "ndt": "",
                "temp": "",
                "pressure": ""
            },
            "components": {}
        }

        component_index = 1

        for item in data:
            component_name, component_data = next(iter(item.items()))

            # --- Common model_info extraction ---
            model_info = component_data.get("model_info", {})
            if model_info:
                standard_model["reactor"] = model_info.get("model", "")
                standard_model["model"] = model_info.get("reactor", "")
                standard_model["model_info"]["glass"] = model_info.get("glass", "")
                standard_model["model_info"]["ndt"] = model_info.get("ndt", "")
                standard_model["model_info"]["temp"] = model_info.get("designTemperature", "")
                standard_model["model_info"]["pressure"] = model_info.get("designPressure", "")

            configurations = {}

            # --- Component-specific parsing logic ---
            if component_name.lower() == "monoblock":
                configurations = {
                    "id": component_data.get("id", ""),
                    "osTOos": component_data.get("osTos", ""),
                    "insulation_on_top": component_data.get("insulationOnTop", ""),
                    "spillage_collection_tray": component_data.get("spilageCollectionTray", ""),
                    "lifting_moc": component_data.get("liftingMOC", ""),
                    "top_dished_end_thickness": component_data.get("topDishedEndThickness", ""),
                    "inner_shell_thickness": component_data.get("innerShellThickness", ""),
                    "bottom_dished_end_thickness": component_data.get("bottomDishedEndThickness", ""),
                    "drawing_number": model_info.get("drawingNumber", ""),
                    "item_code": model_info.get("itemCode", "")
                }

                # Parse nozzles (JSON strings)
                nozzles = {}
                for k, v in component_data.items():
                    if k.startswith("nozzle_"):
                        try:
                            nozzle_dict = json.loads(v)
                            idx = len(nozzles) + 1
                            nozzles[str(idx)] = {
                                "nozzle_name": nozzle_dict.get("nozzleNo", ""),
                                "size": nozzle_dict.get("size", ""),
                                "drilling_standard": nozzle_dict.get("drillingStandard", ""),
                                "degree": nozzle_dict.get("degree", ""),
                                "radius": nozzle_dict.get("radius", ""),
                                "location": nozzle_dict.get("location", ""),
                                "fittings": nozzle_dict.get("fittings", {})
                            }
                        except json.JSONDecodeError:
                            continue
                configurations["nozzles"] = nozzles

            elif component_name.lower() == "jacket":
                jacket_data = component_data.get("jacket", {})
                support_data = component_data.get("support", {})
                earthing_data = component_data.get("earthing", {})
                nozzle_list = component_data.get("nozzles", [])

                configurations = {
                    "jacket": jacket_data,
                    "support": support_data,
                    "earthing": earthing_data,
                }

                # Add jacket nozzles
                nozzles = {}
                for i, n in enumerate(nozzle_list, start=1):
                    nozzles[str(i)] = {
                        "nozzle_name": n.get("nozzle", ""),
                        "size": n.get("size", ""),
                        "degree": n.get("degree", ""),
                        "location": n.get("location", ""),
                        "drawing_number": n.get("drawingNumber", ""),
                        "item_code": n.get("itemCode", "")
                    }
                configurations["nozzles"] = nozzles

            elif component_name.lower() == "diaphragmring":
                configurations = {
                    "ring_material": component_data.get("ringMaterial", ""),
                    "nozzle_size": component_data.get("nozzleSize", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }

            elif component_name.lower() == "springbalanceassembly":
                configurations = {
                    "assembly_name": component_data.get("mhCoverBalanceAssembly", ""),
                    "assembly_size": component_data.get("springbalanceassemblySize", ""),
                    "assembly_type": component_data.get("springbalanceassemblyType", ""),
                    "assembly_material": component_data.get("springbalanceassemblyMaterial", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }

            elif component_name.lower() == "mhcclamp":
                configurations = {
                    "material": component_data.get("mhCClampMaterial", ""),
                    "size": component_data.get("mhCClampSize", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }

            elif component_name.lower() == "coc":
                configurations = {
                    "coc_size": component_data.get("cocSize", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }
            
            elif component_name.lower() == "bfcclamp":
                configurations = {
                    "material": component_data.get("bfCClampMaterial", ""),
                    "size": component_data.get("bfCClampSize", ""),
                    "quantity": component_data.get("bfCClampQty", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "sensor":
                dial_thermo = component_data.get("dialThermo", {})
                configurations = {
                    "sensor_type": dial_thermo.get("sensorType", ""),
                    "length": dial_thermo.get("dialThermoLength", ""),
                    "drawing_number": dial_thermo.get("dialThermoDrawingNumber", ""),
                    "item_code": dial_thermo.get("dialThermoItemCode", "")
                }

            elif component_name.lower() == "agitator":
                single_flight = component_data.get("singleFlightData", {})
                double_flight = component_data.get("doubleFlightData", {})
                triple_flight = component_data.get("tripleFlightData", {})
                special_flight = component_data.get("specialFlightData", {})

                configurations = {
                    "shaft_dia": component_data.get("shaftDia", ""),
                    "sealing_type": component_data.get("sealingType", ""),
                    "volume_marking": component_data.get("volumeMarking", ""),
                    "hastalloy_sleeve": component_data.get("hastalloySleeve", ""),
                    "agitator_height": component_data.get("agitatorHeight", ""),
                    "flight": component_data.get("flight", ""),
                    "single_flight": single_flight,
                    "double_flight": double_flight,
                    "triple_flight": triple_flight,
                    "special_flight": special_flight,
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "shaftclosure":
                configurations = {
                    "shaft_dia": component_data.get("shaftclosureDia", ""),
                    "type": component_data.get("shaftclosureType", ""),
                    "make": component_data.get("shaftclosureMake", ""),
                    "sealing": component_data.get("shaftclosureSealing", ""),
                    "housing": component_data.get("shaftclosureHousing", ""),
                    "inboard_face": component_data.get("shaftclosureInboardFace", ""),
                    "outboard_face": component_data.get("shaftclosureOutboardFace", ""),
                    "other": component_data.get("shaftclosureOther", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "gearbox":
                configurations = {
                    "make": component_data.get("gearboxMake", ""),
                    "type": component_data.get("gearboxType", ""),
                    "model": component_data.get("gearboxModel", ""),
                    "ratio": component_data.get("gearboxRatio", ""),
                    "frame": component_data.get("gearboxFrame", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "motor":
                configurations = {
                    "make": component_data.get("motorMake", ""),
                    "type": component_data.get("motorType", ""),
                    "mounting": component_data.get("motorMouting", ""),
                    "hp": component_data.get("motorHP", ""),
                    "standard": component_data.get("motorStandard", ""),
                    "frame": component_data.get("motorFrame", ""),
                    "temp_class": component_data.get("motorTempClass", ""),
                    "gas_group": component_data.get("motorGasGroup", ""),
                    "protection": component_data.get("motorProtection", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "driveassembly":
                configurations = {
                    "drive_base_ring": component_data.get("driveBaseRing", {}),
                    "pad_plate": component_data.get("padPlat", {}),
                    "lantern_support": component_data.get("lanternSupport", {}),
                    "lantern_guard": component_data.get("lanternGuard", {}),
                    "agitator_gear_coupling": component_data.get("agitatorGearCoupling", {}),
                    "adapter_gearbox_model": component_data.get("adaptorGearBoxModel", {}),
                    "bearing": component_data.get("bearing", {}),
                    "sleeve": component_data.get("sleeve", {}),
                    "oil_seal": component_data.get("oilSeal", {}),
                    "circlip": component_data.get("circlip", {}),
                    "lock_nut": component_data.get("lockNut", {}),
                    "lock_washer": component_data.get("lockWasher", {}),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "nameplatebracket":
                configurations = {
                    "material": component_data.get("npbMaterial", ""),
                    "type": component_data.get("npbType", ""),
                    "mounting": component_data.get("npbMounting", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "airventcouplingplug":
                nozzles = {}
                for i, n in enumerate(component_data.get("nozzles", []), start=1):
                    nozzles[str(i)] = {
                        "nozzle_name": n.get("nozzle", ""),
                        "type": n.get("type", ""),
                        "location": n.get("location", ""),
                        "length": n.get("length", ""),
                        "size": n.get("size", ""),
                        "material": n.get("material", ""),
                        "drawing_number": n.get("drawingNumber", ""),
                        "item_code": n.get("itemCode", "")
                    }

                configurations = {
                    "nozzles": nozzles,
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }


            else:
                # fallback: include all simple key-values
                configurations = {k: v for k, v in component_data.items() if not isinstance(v, (dict, list))}

            # Add component into main dict
            standard_model["components"][str(component_index)] = {
                "component": component_name,
                "configurations": configurations
            }
            component_index += 1

        return standard_model
    
    def extract_component_data(self, data: dict):
        """
        Extract standardized component and subcomponent data
        from a standard model dictionary. 
        """

        results = []
        id_counter = 1

        def make_entry(comp, itemcode, drawing_number, subs=None):
            nonlocal id_counter
            entry = {
                "id": id_counter,
                "comp": comp.lower(),
                "partnumber": drawing_number or "",
                "member": "",
                "itemcode": itemcode or "",
                "sub_components": subs or []
            }
            id_counter += 1
            return entry

        components = data.get("components", {})

        for key, comp_data in components.items():
            comp_name = comp_data.get("component", "").lower()
            config = comp_data.get("configurations", {})

            # --- MONOBLOCK ---
            if comp_name == "monoblock":
                results.append(make_entry(
                    "monoblock",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- JACKET (has nested parts) ---
            elif comp_name == "jacket":
                jacket = config.get("jacket", {})
                support = config.get("support", {})
                earthing = config.get("earthing", {})

                results.append(make_entry(
                    "jacket",
                    jacket.get("itemCodeJacket"),
                    jacket.get("drawingNumberJacket")
                ))

                if support:
                    results.append(make_entry(
                        support.get("component", "sidebracket"),
                        support.get("itemCodeJacketSupport"),
                        support.get("drawingNumberJacketSupport")
                    ))

                if earthing:
                    results.append(make_entry(
                        "earthing",
                        earthing.get("itemCodeJacketEarthing"),
                        earthing.get("drawingNumberJacketEarthing")
                    ))

            # --- DIAPHRAGMRING ---
            elif comp_name == "diaphragmring":
                results.append(make_entry(
                    "diaphragmring",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- SPRING BALANCE ASSEMBLY ---
            elif comp_name == "springbalanceassembly":
                results.append(make_entry(
                    "springbalanceassembly",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- MHC CLAMP / BF C CLAMP ---
            elif comp_name in ["mhcclamp", "bfCClamp".lower()]:
                results.append(make_entry(
                    comp_name,
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- SENSOR ---
            elif comp_name == "sensor":
                results.append(make_entry(
                    "sensor",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- COC ---
            elif comp_name == "coc":
                results.append(make_entry(
                    "coc",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- AGITATOR ---
            elif comp_name == "agitator":
                results.append(make_entry(
                    "agitator",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- SHAFT CLOSURE ---
            elif comp_name == "shaftclosure":
                results.append(make_entry(
                    "shaftclosure",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- GEARBOX ---
            elif comp_name == "gearbox":
                results.append(make_entry(
                    "gearbox",
                    "",
                    ""
                ))
                # results.append(make_entry(
                #     "gearbox",
                #     config.get("item_code"),
                #     config.get("drawing_number")
                # ))

            # --- MOTOR ---
            elif comp_name == "motor":
                results.append(make_entry(
                    "motor",
                    "",
                    ""
                ))
                # results.append(make_entry(
                #     "motor",
                #     config.get("item_code"),
                #     config.get("drawing_number")
                # ))

            # --- DRIVE ASSEMBLY (multi-sub) ---
            elif comp_name == "driveassembly":
                subconfigs = config
                for sub_name, sub_conf in subconfigs.items():
                    if isinstance(sub_conf, dict):
                        # if sub_name == "drive_base_ring":
                        results.append(make_entry(
                            sub_name,
                            "",
                            ""
                        ))
                        # results.append(make_entry(
                        #     sub_name,
                        #     sub_conf.get("item_code") or sub_conf.get("itemCode") or sub_conf.get("itemCodeDriveBaseRing") or sub_conf.get("itemCodePadPlate") or sub_conf.get("itemCodeLanternSupport") or sub_conf.get("itemCodeLanternGuard") or sub_conf.get("itemCodeAgitatorGearCoupling") or sub_conf.get("itemCodeGearBoxModel") or sub_conf.get("itemCodeBearingNumber") or sub_conf.get("itemCodeSleeve") or sub_conf.get("itemCodeOilSeal") or sub_conf.get("itemCodeCirclip") or sub_conf.get("itemCodeLockNut") or sub_conf.get("itemCodeLockWasher"),
                        #     sub_conf.get("drawing_number") or sub_conf.get("drawingNumber") or sub_conf.get("drawingNumberDriveBaseRing") or sub_conf.get("drawingNumberPadPlate") or sub_conf.get("drawingNumberLanternSupport") or sub_conf.get("drawingNumberLanternGuard") or sub_conf.get("drawingNumberAgitatorGearCoupling") or sub_conf.get("drawingNumberGearBoxModel") or sub_conf.get("drawingNumberBearingNumber") or sub_conf.get("drawingNumberSleeve") or sub_conf.get("drawingNumberOilSeal") or sub_conf.get("drawingNumberCirclip") or sub_conf.get("drawingNumberLockNut") or sub_conf.get("drawingNumberLockWasher")
                        # ))

            # --- NAME PLATE BRACKET ---
            elif comp_name == "nameplatebracket":
                results.append(make_entry(
                    "nameplatebracket",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))

            # --- AIR VENT COUPLING PLUG (nozzles) ---
            elif comp_name == "airventcouplingplug":
                nozzles = config.get("nozzles", {})
                for nz_key, nz_data in nozzles.items():
                    results.append(make_entry(
                        f"airvent_{nz_data.get('type', '').lower()}_{nz_data.get('nozzle_name', '').lower()}",
                        nz_data.get("item_code"),
                        nz_data.get("drawing_number")
                    ))

            # --- DEFAULT / FALLBACK ---
            else:
                # try generic item_code / drawing_number if nothing matches
                itemcode = config.get("item_code") or next(
                    (v for k, v in config.items() if "itemcode" in k.lower()), "")
                drawing_number = config.get("drawing_number") or next(
                    (v for k, v in config.items() if "drawing" in k.lower()), "")
                results.append(make_entry(comp_name, itemcode, drawing_number))
           
        # results = [c for c in results if c.get("itemcode")]

        return results

    def generate_model(self, model_details):
        components = self.get_component_list(model_details=model_details)
        standard_model = self.build_standard_model(data = components)
        # result_id = self.mongo.insert(collection_name="standard_models", document=standard_model)
        result = self.extract_component_data(data=standard_model)
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
                                {'id':9, 'comp': 'baffle_plate', 'partnumber': '', 'member': '', 'itemcode':'3502B0108', 'sub_components': []}, # add to jacket nozzle for btm
                                {'id':9.1, 'comp': 'baffle_bend_plate', 'partnumber': '', 'member': '', 'itemcode':'3502B0099', 'sub_components': []}, # add to jacket nozzle for shell

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
        # downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=component_item_codes)
        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=result)
        is_generated = self.inventor.generate(components=downloaded_components_files, model_details=model_details)
        return is_generated
    def open_component(self, compo_details):
        components = self.get_component_list(model_details=compo_details)
        item_code = self.get_item_code_by_component(components=components, comp_details=compo_details)
        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=item_code)
        print(downloaded_components_files)
        result = self.inventor.open(downloaded_components_files)
        return result