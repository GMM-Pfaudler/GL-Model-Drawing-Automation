import pandas as pd
import os
import json
from decimal import Decimal, InvalidOperation

class Components:
    def __init__(self):
        self.file_path = None
        pass

    def saveToExcel(self, data):
        try:
            component = list(data.keys())[0]
            model_info = data.get(component, {}).get('model_info', {})
            model_capacity = model_info.get('capacity')
            model_type_raw = model_info.get('model', '')

            if not model_capacity or not model_type_raw:
                raise ValueError("Missing required model info: 'capacity' or 'model'")

            model_type = model_type_raw.split('_')[0]
            if component == 'cleat' or component == 'nut' or component == 'tophead' or component == 'topjcr' or component == 'head' or component == 'shell' or component == 'closer':
                file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\insulation\\{component}.xlsx"
            elif component == 'drivebasering' or component == 'padplate' or component == 'lanternsupport' or component == 'lanternguard' or component == 'agitatorgearcoupling' or component == 'gearboxmodel' or component == 'bearingnumber' or component == 'sleeve' or component == 'oilseal' or component == 'circlip' or component == 'locknut' or component == 'lockwasher':
                file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\driveAssembly\\{component}.xlsx"
            elif component == 'jacket' or component == 'jacketnozzle' or component == 'earthing' or component == 'sidebracket' or component == 'legsupport' or component == 'sidebracketlegsupport' or component == 'ringsupport' or component == 'skirtsupport':
                file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\jacket\\{component}.xlsx"
            else:
                file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\{component}\\{component}.xlsx"

            self.file_path = file_path  # Save for other usage

            flat_data = self.flatten_dict(d=data)
            df_new = pd.DataFrame([flat_data])

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if os.path.exists(file_path):
                try:
                    df_existing = pd.read_excel(file_path)
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.to_excel(file_path, index=False)
                    print(f"Data appended to existing file '{file_path}'.")
                    return True
                except Exception as e:
                    print(f"Failed to read or append to existing file: {e}")
                    return False
            else:
                try:
                    df_new.to_excel(file_path, index=False)
                    print(f"New file '{file_path}' created with data.")
                    return True
                except Exception as e:
                    print(f"Failed to create new Excel file: {e}")
                    return False

        except (KeyError, ValueError) as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as ex:
            print(f"Unexpected error occurred: {ex}")
            return False

    def flatten_dict(self, d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            if k == 'component':  # ✅ skip this key
                continue
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


    # def flatten_dict(self, d, parent_key='', sep='.'):
    #     items = []
    #     for k, v in d.items():
    #         new_key = f"{parent_key}{sep}{k}" if parent_key else k
    #         if isinstance(v, dict):
    #             items.extend(self.flatten_dict(v, new_key, sep=sep).items())
    #         else:
    #             items.append((new_key, v))
    #     return dict(items)
    
    def read_file_and_unflatten_dict(self, file_path, sep='.'):
        df = pd.read_excel(file_path)
        # Read the first row (you can loop through all rows if needed)
        flat_dict = df.iloc[0].dropna().to_dict()
        result = {}
        for compound_key, value in flat_dict.items():
            keys = compound_key.split(sep)
            d = result
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            d[keys[-1]] = value
        return result
    
    def normalize_value(self, value):
        """
        Convert value to lowercase stripped string,
        and try to normalize numeric strings to Decimal for consistent comparison.
        """
        if value is None:
            return None
        str_val = str(value).strip().lower()
        if str_val in ('', 'none', 'nan'):
            return None
        try:
            # Convert numeric-like values to Decimal
            return Decimal(str_val)
        except InvalidOperation:
            return str_val  # Return as-is for non-numeric values

    def match_row_and_get_item_code(self, df, flat_input):
        item_code_column = [key for key in flat_input.keys() if 'model_info.itemCode' in key][0]
        drawing_number_column = [key for key in flat_input.keys() if 'model_info.drawingNumber' in key][0]

        flat_input_filtered = {
            k: self.normalize_value(v)
            for k, v in flat_input.items()
            if k not in (item_code_column, drawing_number_column)
            and self.normalize_value(v) is not None
        }

        for _, row in df.iterrows():
            row_dict = row.dropna().to_dict()

            row_filtered = {
                k: self.normalize_value(v)
                for k, v in row_dict.items()
                if k not in (item_code_column, drawing_number_column)
            }

            match = True
            for key, input_value in flat_input_filtered.items():
                row_value = row_filtered.get(key)
                if row_value != input_value:
                    match = False
                    break

            if match:
                return {
                    "itemCode": row_dict.get(item_code_column),
                    "drawingNumber": row_dict.get(drawing_number_column)
                }

        return None

    def search_item_code(self, data):
        try:
            component = list(data.keys())[0]
            model_info = data.get(component, {}).get('model_info', {})
            model_capacity = model_info.get('capacity')
            model_type_raw = model_info.get('model', '')

            if not model_capacity or not model_type_raw:
                raise ValueError("Missing required model info: 'capacity' or 'model'")

            model_type = model_type_raw.split('_')[0]
            if component == 'cleat' or component == 'nut' or component == 'tophead' or component == 'topjcr' or component == 'head' or component == 'shell' or component == 'closer':
                self.file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\insulation\\{component}.xlsx"
            elif component == 'drivebasering' or component == 'padplate' or component == 'lanternsupport' or component == 'lanternguard' or component == 'agitatorgearcoupling' or component == 'gearboxmodel' or component == 'bearingnumber' or component == 'sleeve' or component == 'oilseal' or component == 'circlip' or component == 'locknut' or component == 'lockwasher':
                self.file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\driveAssembly\\{component}.xlsx"
            elif component == 'jacket' or component == 'jacketnozzle' or component == 'earthing' or component == 'sidebracket' or component == 'legsupport' or component == 'sidebracketlegsupport' or component == 'ringsupport' or component == 'skirtsupport':
                self.file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\jacket\\{component}.xlsx"
            else:
                self.file_path = f"D:\\GL\\{model_type}\\{model_capacity}\\{component}\\{component}.xlsx"

            if not os.path.exists(self.file_path):
                print(f"File not found: {self.file_path}")
                return {"result": None}

            flat_input = self.flatten_dict(d=data)

            try:
                df = pd.read_excel(self.file_path)
            except Exception as e:
                print(f"Failed to read Excel file '{self.file_path}': {e}")
                return {"result": None}

            matched = self.match_row_and_get_item_code(df=df, flat_input=flat_input)
            return {"result": matched}
        except (KeyError, ValueError) as ve:
            print(f"Validation error: {ve}")
            return {"result": None}
        except Exception as ex:
            print(f"Unexpected error occurred: {ex}")
            return {"result": None}
        
    @staticmethod
    def save_component_progress(payload: dict):
        import os
        import pandas as pd

        try:
            # Extract payload
            data = payload.get("component_data", {})
            id_prefix = payload.get("id_prefix", "ASB")
            model_type = payload.get("model_type", "")
            capacity = payload.get("capacity", "")
            component_name = payload.get("component_name", "component")

            # Flatten component data into a single dict row
            flat_row = {}
            for comp, vals in data.items():
                flat_row[f"{comp}.drawing_number"] = vals.get("drawing_number")
                flat_row[f"{comp}.item_code"] = vals.get("item_code")

            print(f"Model Type:- {model_type}")
            print(f"Model capacity:- {capacity}")
            print(f"Component name:- {component_name}")

            # Build folder path
            base_dir = os.path.join("D:\\GL", model_type, capacity, component_name)
            os.makedirs(base_dir, exist_ok=True)

            # Excel file path (single file per component)
            excel_path = os.path.join(base_dir, f"{component_name}fullcomponent.xlsx")

            # If file doesn't exist → create new
            if not os.path.exists(excel_path):
                unique_id = f"{id_prefix}0001"
                df = pd.DataFrame([{"Unique ID": unique_id, **flat_row}])
                df.to_excel(excel_path, index=False)
                print(f"✅ Created new Excel: {excel_path}")
                return {"unique_id": unique_id, "status": "new", "file_path": excel_path}

            # Load existing Excel
            df = pd.read_excel(excel_path)

            # Ensure Unique ID column exists
            if "Unique ID" not in df.columns:
                df.insert(0, "Unique ID", None)

            # Keep schema consistent
            df = df[[c for c in df.columns if c in ["Unique ID"] + list(flat_row.keys())]]

            # Check if this combination already exists
            mask = (df.drop(columns=["Unique ID"]).fillna("").astype(str) ==
                    pd.Series(flat_row).fillna("").astype(str)).all(axis=1)
            existing_rows = df[mask]

            if not existing_rows.empty:
                unique_id = existing_rows.iloc[0]["Unique ID"]
                print(f"✅ Existing combination found: {unique_id}")
                return {"unique_id": unique_id, "status": "existing", "file_path": excel_path}

            # Generate new unique ID
            existing_ids = df["Unique ID"].dropna().astype(str)
            existing_nums = [int(i.replace(id_prefix, "")) for i in existing_ids if i.startswith(id_prefix)]
            last_num = max(existing_nums) if existing_nums else 0
            new_num = last_num + 1
            unique_id = f"{id_prefix}{new_num:04d}"

            # Append new row
            new_row = {"Unique ID": unique_id, **flat_row}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(excel_path, index=False)

            print(f"✅ Added new entry: {unique_id} in {excel_path}")
            return {"unique_id": unique_id, "status": "new", "file_path": excel_path}

        except Exception as e:
            print(f"❌ Error in save_component_progress: {e}")
            return {"unique_id": None, "status": "error"}

    def save_to_json(self, component_details):
        """
        Updates or appends a dictionary in a JSON file based on a unique key.

        - Creates the folder and file if they don't exist.
        - Updates existing entry based on a match key, or appends if not found.
        - Wraps new_data as {match_key: new_data}
        """

        keys = list(component_details['componentDetails'].keys())
        if len(keys) < 2:
            print("Invalid component_details structure")
            return False

        so_value = component_details['componentDetails'][keys[1]]
        folder_name = f"D:\\GL\\SO\\{so_value}"
        file_path = f"{folder_name}\\{so_value}.json"
        match_key = keys[0]
        new_data = component_details['componentDetails'][match_key]

        # 👇 Wrap new_data as {match_key: new_data}
        wrapped_data = {match_key: new_data}
        data_list = []

        # ✅ Ensure folder exists
        os.makedirs(folder_name, exist_ok=True)

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
                return False

        # ✅ Update or append
        updated = False
        for i, item in enumerate(data_list):
            if isinstance(item, dict) and match_key in item:
                if item[match_key].get(match_key) == new_data.get(match_key):
                    data_list[i] = wrapped_data
                    updated = True
                    break

        if not updated:
            data_list.append(wrapped_data)

        # ✅ Save back to file
        try:
            with open(file_path, 'w') as file:
                json.dump(data_list, file, indent=2)
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False