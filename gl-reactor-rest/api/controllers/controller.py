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
    
@router.post("/generate")
async def generate_model(request: Request):
    try:
        details = await request.json()
        result = generation_service.generate_model(model_details=details)
        return {"r": result}
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
    