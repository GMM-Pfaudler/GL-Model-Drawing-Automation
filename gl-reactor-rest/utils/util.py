# import base64
# import json,os,sys
 
# from openai import OpenAI

# client = OpenAI(base_url = 'http://localhost:11434/v1', api_key="ollama")

# def image_to_base64(image_path):
#     if not os.path.exists(image_path):
#         # Using sys.stderr for error messages, so only the Base64 string goes to stdout
#         sys.stderr.write(f"Error: File not found at '{image_path}'\n")
#         return None

#     try:
#         with open(image_path, 'rb') as image_file:
#             image_bytes = image_file.read()
#             base64_encoded_data = base64.b64encode(image_bytes)
#             base64_string = base64_encoded_data.decode('utf-8')
#             return base64_string

#     except Exception as e:
#         sys.stderr.write(f"An error occurred during conversion: {e}\n")
#         return None
    
# base_64_image = image_to_base64(r"glens-backend\app\GLE004147-1_CERIM-6.3KL_pages-to-jpg-0001 (1).jpg")

# def get_details_from_image(base64_image):
#     if not base64_image:
#         return None
 
#     response = client.chat.completions.create(
#         model="qwen3-vl:235b-cloud",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "Extract details from the given image.\n"
#                     "Instructions:\n"
#                     "WIND LOAD, NOZZLE NECKS, DESIGN CODE"
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ]
#     )
 
#     try:
#         result_content = response.choices[0].message.content
#         return json.loads(result_content)
#     except (IndexError, AttributeError, json.JSONDecodeError):
#         return None
    
# result = get_details_from_image(base64_image=base_64_image)
# print(result)