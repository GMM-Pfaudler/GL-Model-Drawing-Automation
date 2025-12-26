import os
import glob
import json
import re
import win32com.client
import asyncio
from toon import encode
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # api_key="51fbc177e92d4e55ac1169446a4f689d.K_9zy9Os5PwihIBadheL1677",
    api_key="ollama",
    base_url="http://172.30.0.20:11434/v1"
)

async def extract_nozzles_via_llm(params):
    """
    Send Inventor parameters to an LLM to extract dish thickness, 
    nozzle info, and nozzle count.
    """

    # Convert params to JSON string to send to LLM
    # param_str = json.dumps(params)
    params_string = encode(params)
    prompt = """
        You are an expert JSON-structured data extraction engine. Follow all rules exactly.
        Never add extra fields, never omit required fields, and return ONLY the final JSON output.

        ---------------------- TASK ----------------------

        You will receive a TOON text string (not JSON).  
        This TOON string contains multiple parameter definitions in the form:

            name: <NAME>
            expression: <VALUE>

        Your job is to parse this TOON string and extract data exactly as described below.

        ==================== 1. Nozzle Extraction ====================
        Identify nozzles whose names match these patterns:

        - Names beginning with N{{digit}}
        - Names beginning with A{{digit or alphabet}}
        - Names beginning with N{{digit + letter or underscore}}

        Examples of valid nozzle identifiers:
            N1, N2, N3A, N4_TOP, N6_x, A1, A2B, N10, N3_C, N7A, N7B

        For each nozzle:
        Extract parameters ONLY if they exist:
            <NOZZLE>_DIA or <NOZZLE>_DIA{{digit}}
            <NOZZLE>_DEGREE or <NOZZLE>_DEG or <NOZZLE>_DEGREE{{digit}}
            <NOZZLE>_RADIUS or <NOZZLE>_RADIUS{{digit}}

        Return each nozzle as:

        "<NOZZLE>": {{
            "dia": {{
                "expression": "...",
            }},
            "degree": {{
                "expression": "...",
            }},
            "radius": {{
                "expression": "...",
            }}
        }}

        If a field (dia/degree/radius) is missing for a nozzle, omit it.

        ==================== 2. Nozzle Count ====================
        Count only real nozzles matching patterns:
            N{{digit}}, A{{digit/char}}, N{{digit+letter/underscore}}

        Do NOT count dish_thk.

        ==================== 3. Output Format (STRICT) ====================
        Return ONLY the final JSON result:

        {{
        "nozzles": {{
            "<NOZZLE1>": {{ ... }},
            "<NOZZLE2>": {{ ... }}
        }},
        "nozzle_count": <integer>
        }}

        NO explanation.
        NO comments.
        NO extra text.

        ---------------------- INPUT TOON STRING ----------------------

        {toon_string}

        ---------------------- END ----------------------

        """
    prompt = prompt.format(toon_string=params_string)

    try:
        response = await client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

    # Extract output text and parse JSON
    
        output_text = response.choices[0].message.content
        if output_text is not None:
            res = "\n".join(line for line in output_text.splitlines() if not line.startswith("```"))
            return json.loads(res)
        return None
    except Exception as e:
        print("Error parsing LLM output:", e)
        return None

def find_occurrence_recursive(occurrences, target_name):
    """Recursively find an occurrence by name (case-insensitive)."""
    target_lower = target_name.lower()
    for occ in occurrences:
        name = occ.Name.lower()
        if hasattr(occ, 'Definition'):
            display_name = occ.Definition.Document.DisplayName.lower()
            if target_lower in name or target_lower in display_name:
                return occ
            if hasattr(occ, "SubOccurrences") and occ.SubOccurrences.Count > 0:
                found = find_occurrence_recursive(occ.SubOccurrences, target_name)
                if found:
                    return found
    return None

def get_monoblock_part_number(doc):
    try:
        # Confirm the occurrence has a valid Definition
        if not hasattr(doc, 'PropertySets') or doc.PropertySets is None:
            return ""
        part_number = doc.PropertySets['Design Tracking Properties']['Part Number'].Value
        return part_number
    except Exception as e:
        print("Error while extracting part number from document.", str(e))
        return ""

def get_monoblock_item_code(doc):
    try:
        # Confirm the occurrence has a valid Definition
        if not hasattr(doc, 'PropertySets') or doc.PropertySets is None:
            return ""
        keywords = doc.PropertySets['Summary Information']['KeyWords'].Value
        return keywords
    except Exception as e:
        print("Error while extracting item code from document.", str(e))
        return ""
    
def get_dish_thikness(fabricated_body):
    dish_thk = None
    if hasattr(fabricated_body, 'Definition'):
        dish_thk_description = fabricated_body.Definition.Document.PropertySets['Design Tracking Properties']['Description'].Value
        dish_thk = None
        if 'STD' in dish_thk_description:
            dish_thk = "20 mm"
    
    return dish_thk

def parse_component_string(s: str):
    # Split at space first to isolate primary code part
    first_part = s.split()[0]
    
    # Split by hyphens
    parts = first_part.split('-')
    # Expected: ['CT', '1950', '20', 'STD', 'IH', '00', 'R0_SWAGGED', ...]
    
    result = {}

    # CE Type
    result['Type'] = parts[0]  # CT
    
    # Inside Diameter (I/D)
    result['ID'] = parts[1]
    
    # Dish Thickness
    if parts[3] == 'STD':
        result['TOP_DISH_THK'] = str(20)
    else:
        result['TOP_DISH_THK'] = parts[2]
    
    # In-House Manufactured
    result['In_House'] = (parts[4] == 'IH')
    
    # Version / additional code
    result['Additional_Code'] = "-".join(parts[5:])
    
    return result

def parse_bottom_component(s: str):
    # Split at first space to isolate primary code section
    first_part = s.split()[0]   # "BTM-1950-20-150-IH-00"
    
    # Split by hyphens
    parts = first_part.split('-')
    # Expected: ['BTM', '1950', '20', '150', 'IH', '00']
    
    result = {}
    
    # Type (BTM = bottom)
    result['Type'] = parts[0]   # BTM
    
    # Inner Diameter
    result['ID'] = parts[1]
    
    # Bottom Dish Thickness
    result['BTM_DISH_THK'] = parts[2]
    
    # Bottom Dish Nozzle Diameter
    result['BTM_NOZZLE_DIA'] = parts[3]
    
    # In-House Manufactured
    result['In_House'] = (parts[4] == 'IH')
    
    # Additional Code
    result['Additional_Code'] = parts[5]
    
    # Remaining descriptor after space (if exists)
    # remainder = " ".join(s.split()[1:])  # everything after first space
    # result['Remainder'] = remainder if remainder else None
    
    return result

def get_lifting_moc_material(lifting_moc):
    if hasattr(lifting_moc, 'Definition'):
        moc_material = lifting_moc.Definition.Document.PropertySets['Design Tracking Properties']['Material'].Value
        return {'moc_material': moc_material}
    return {'moc_material': None}

def extract_inner_shell_thk(inner_shell: str):
    """
    Extracts the number immediately before the letter 'T' (e.g., 18T -> 18).
    Returns integer thickness or None if not found.
    """
    match = re.search(r'(\d+)T', inner_shell, re.IGNORECASE)
    return {"INNER_SHELL_THK": match.group(1)} if match else {"INNER_SHELL_THK": None}

async def process_inventor_files_llm(root_dir, file_limit=10):
    """Process Inventor IAM files and use LLM to extract nozzle info."""
    iam_files = glob.glob(os.path.join(root_dir, "**", "MBCE*.iam"), recursive=True)

    inv = win32com.client.Dispatch("Inventor.Application")
    inv.Visible = False
    inv.SilentOperation = True

    results = []

    for path in iam_files[:file_limit]:
        try:
            print(path)
            # path = r"D:\Vault\Designs\SUB ASSEMBLY\INNER BODY\GL INNER BODY\CE-6.3KL\MBCE-06300-2020-003 R0_GL INNER BODY CE-6.3KL.iam"
            doc = inv.Documents.Open(path)
            if doc:
                item_code = get_monoblock_item_code(doc=doc)
                part_number = get_monoblock_part_number(doc=doc)
                # dish_thk = get_dish_thikness(fabricated_body=fabricated_body)
                top_dish = find_occurrence_recursive(doc.ComponentDefinition.Occurrences, "CT-")
                inner_shell = find_occurrence_recursive(doc.ComponentDefinition.Occurrences, "INNER SHELL")
                btm_dish = find_occurrence_recursive(doc.ComponentDefinition.Occurrences, "BTM-")
                spilage_collection_tray = find_occurrence_recursive(doc.ComponentDefinition.Occurrences, "6THK RING")
                lifting_moc = find_occurrence_recursive(doc.ComponentDefinition.Occurrences, "LL-")
                name_plate_bracket = find_occurrence_recursive(doc.ComponentDefinition.Occurrences, "NAME PLATE BRACKET")
                
                if top_dish:
                    top_dish_details = parse_component_string(s = top_dish.Name)
                    inner_shell_thickness = extract_inner_shell_thk(inner_shell=inner_shell.Name)
                    btm_dish_details = parse_bottom_component(s = btm_dish.Name)
                    lifting_moc_material = get_lifting_moc_material(lifting_moc)
                    params = [
                        {
                            "name": param.Name,
                            "expression": param.Expression
                        }
                        for param in top_dish.Definition.Parameters
                        if hasattr(param, "Name")
                        and re.match(r"^[NM]", param.Name)         # keep only names starting with N or M
                        and not re.search(r"R\d", param.Name)      # ignore names containing R followed by a digit
                    ]

                    monoblock_data = {}
                    # Send parameters to LLM for extraction
                    nozzles_details = await extract_nozzles_via_llm(params)
                    nozzles_details["nozzles"] = {k: v for k, v in nozzles_details["nozzles"].items() if v}; nozzles_details["nozzle_count"] = len(nozzles_details["nozzles"])
                    monoblock_data['nozzles_details'] = nozzles_details
                    nozzles_details['nozzle_count'] = nozzles_details['nozzle_count'] + 1
                    monoblock_data['top_dish_thk'] = top_dish_details['TOP_DISH_THK']
                    monoblock_data['inner_shell_thk'] = inner_shell_thickness['INNER_SHELL_THK']
                    monoblock_data['btm_dish_details'] = btm_dish_details['BTM_DISH_THK']
                    monoblock_data['spilage_collection_tray'] = "Yes" if spilage_collection_tray is not None else "No"
                    monoblock_data['insulation_on_top'] = "Yes" if name_plate_bracket is not None and "insulation" in name_plate_bracket.Name.lower() else "No"
                    monoblock_data['lifting_moc_material'] = lifting_moc_material['moc_material']
                    
                    results.append({
                        "file_path": path,
                        "component_name": doc.ComponentDefinition.Document.DisplayName,
                        "item_code": item_code,
                        "drawing_number": part_number,
                        **(monoblock_data or {})
                    })

                # doc.Close(True)

        except Exception as e:
            # results.append({"file_path": path, "error": str(e)})
            print("Error: ", str(e))

    return results

async def main():
    root_dir = r"D:\Vault\Designs\SUB ASSEMBLY\INNER BODY\GL INNER BODY\CE-6.3KL"
    data = await process_inventor_files_llm(root_dir)
    print(json.dumps(data, indent=2))

asyncio.run(main())
