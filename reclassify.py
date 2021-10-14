import requests
import json
import pandas as pd

# reading json file from directory
input_path = "C:\\Users\\CeciliaLuna\\Documents\\Reclassify Tool Helpful Documents\\my_documents_input.xlsx"
# out_filename = "C:\\Users\\CeciliaLuna\\Documents\\reclassify_output.csv"

# authenticating
baseurl = "https://vvtechpartner-daelight-clinicalsuite01.veevavault.com/api/v20.3/auth"

payload = {'username': 'cecilia.luna@vvtechpartner-daelight.com',
'password': 'DreamerCS;1125'}
files = [

]
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

response = requests.request("POST", baseurl, headers=headers, params=payload, files=files)
authContent = response.json()
sessionID = authContent['sessionId']

input = pd.read_excel(input_path)

url = "https://vvtechpartner-daelight-clinicalsuite01.veevavault.com/api/v19.1/objects/documents/"

payload = 'type__v=Trial%20Management&subtype__v=Trial%20Oversight&classification__v=Communication%20Plan&lifecycle__v=Base%20Doc%20Lifecycle&reclassify=TRUE'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Authorization': sessionID
}
#
output_df = pd.DataFrame(columns=['id', 'responseStatus', 'errors'])

for index, row in input.iterrows():
    doc_id = str(row['id'])
    reclassify = str(row['reclassify'])
    doc_type = str(row['type__v']).replace(" ", "%20")
    doc_subtype = str(row['subtype__v']).replace(" ", "%20")
    doc_classification = str(row['classification__v']).replace(" ", "%20")
    doc_lifecycle = str(row['lifecycle__v']).replace(" ", "%20")
    full_url = url + doc_id
    parameters = '?type=' + doc_type + '&subtype__v=' + doc_subtype + '&classification__v=' + doc_classification + '&lifecycle__v=' + doc_lifecycle + '&reclassify=' + reclassify
    response = requests.put(full_url, headers=headers, data=parameters)
    print(full_url)
    print(response)
    json_file = response.json()
    print(json_file)
    if json_file['responseStatus'] == 'SUCCESS':
        document_id = json_file['id']
        status = json_file['responseStatus']
        new_row = {'id': document_id, 'responseStatus': status, 'errors': 'No Errors'}
        output_df = output_df.append(new_row, ignore_index=True)
    else:
        status = json_file['responseStatus']
        error = json_file['errors'][0]['message']
        new_row = {'id': document_id, 'responseStatus': status, 'errors': error}
        output_df = output_df.append(new_row, ignore_index=True)

output_df.to_csv(r'C:/Users/CeciliaLuna/Documents/reclassify_output_1.csv', index=False)