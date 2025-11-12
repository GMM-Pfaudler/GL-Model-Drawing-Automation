from fastapi import APIRouter, HTTPException, Request, HTTPException
from services.ofn_service import OFNService
from services.component_service import Components
from services.generation_service import Generation

ofn_service = OFNService()
components_service = Components()
generation_service = Generation()
router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

# OFN Endpoints
@router.post("/getofn")
async def get_ofn_by_sfon(request: Request):
    try:
        sfon_details = await request.json()
        result = ofn_service.get_ofn_by_sfon(sfon=sfon_details['sfon'])
        return {"ofn_details": result}
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with getting ofn details by sfon.')
    
# OFN Endpoints
@router.post("/getmasters")
async def get_masters(request: Request):
    try:
        master_details = await request.json()
        result = ofn_service.get_masters(master_names=master_details)
        return {"master_details": result}
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with getting jacket masters.')
# Components Endpoints   
@router.post("/save")
async def save_component_data(request: Request):
    try:
        component_data = await request.json()
        result = components_service.saveToExcel(data=component_data)
 
        if not result:
            raise HTTPException(status_code=409, detail="Excel file is open or locked. Please close it before saving.")
       
        return result
   
    except HTTPException as http_exc:
        raise http_exc  # Let FastAPI handle it properly
   
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with Saving component details.')
    

# # Components Endpoints
# @router.post("/save")
# async def save_component_data(request: Request):
#     try:
#         component_data = await request.json()
#         result = components_service.saveToExcel(data=component_data)
#         return result
#     except Exception as e:
#         print("Exception: ", e)
#         raise HTTPException(status_code=500, detail='Something went wrong with Saving component details.')
    
@router.post("/search")
async def search_component_data(request: Request):
    try:
        component_data = await request.json()
        result = components_service.search_item_code(data=component_data)
        return result
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with Searching component details.')
    
@router.post("/savetojson")
async def save_to_json(request: Request):
    try:
        component_data = await request.json()
        result = components_service.save_to_json(component_details=component_data)
        return result
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with Saving component details to JSON.')
    
@router.post("/save-component-progress")
async def save_component_progress(request: Request):
    try:
        body = await request.json()  # <-- this is the payload sent by frontend
        print("Received payload:", body)

        # Pass entire payload to the service
        result = components_service.save_component_progress(payload=body)

        # If Excel is locked or cannot be saved
        if not result or result.get("status") == "error":
            raise HTTPException(
                status_code=409,
                detail="Excel file is open or locked. Please close it before saving."
            )

        # Normal success response
        unique_id = result.get("unique_id")
        progress_status = result.get("status")

        return {
            "status": progress_status,       # "new", "existing"
            "unique_id": unique_id,           # "ASBCE_6300L0001", etc.
            "message": (
                "Component progress saved successfully."
                if progress_status == "new"
                else "Component already exists."
            ),
            "file_path": result.get("file_path")  # optional, path to the Excel file
        }

    except HTTPException as http_exc:
        raise http_exc  # Allow FastAPI to handle the 409 gracefully

    except Exception as e:
        print("❌ Exception in /save-component-progress:", e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while saving component progress."
        )

@router.post("/generate")
async def generate_model(request: Request):
    try:
        details = await request.json()
        result = generation_service.generate_model(model_details=details)
        return {"result": result}
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with model generation.')
    
@router.post("/open")
async def open_component(request: Request):
    try:
        details = await request.json()
        result = generation_service.open_component(compo_details=details)
        return {"isOpen": result}
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with model generation.')
    
# OFN Endpoints
@router.post("/getmodel")
async def get_standard_model(request: Request):
    try:
        model_details = await request.json()
        print(model_details)
        # result = ofn_service.get_ofn_by_sfon(sfon=sfon_details['sfon'])
        # return {"ofn_details": result}
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=500, detail='Something went wrong with getting ofn details by sfon.')