import requests
import csv

# (1) Fill in input file directory path within the '' (example:  'C:\Documents\...')
in_filename = 'C:\\Users\\CeciliaLuna\\Downloads\\update_classifications_input.csv'

# (2) Fill in base url for API calls within the ''
baseurl = 'https://sb-gskch-quality.veevavault.com/api/v20.3/auth'

# (3) Fill in username and password for API calls within the ''
username = 'akunz@sb-gskch.com'
password = 'Daffyduck123?'

# (4) Fill in output file directory path within the '' (example:  'C:\Documents\...')
out_filename = ''

authurl = baseurl + '/auth'

credentials = {'username': username, 'password': password}
authResponse = requests.post(authurl, data=None, params=credentials)
authContent = authResponse.json()
print(authContent)
sessionID = authContent['sessionId']
print(sessionID)

url = "https://sb-gskch-quality.veevavault.com/api/v19.1/objects/documents/10"

payload = 'type__v=IRB%20or%20IEC%20and%20other%20Approvals&subtype__v=IRB%20or%20IEC%20Trial%20Approval&classification__v=IRB-EC%20Application%20Form&lifecycle__v=Base%20Doc%20Lifecycle&reclassify=TRUE'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Authorization': sessionID
}

response = requests.request("PUT", url, headers=headers, data=payload)

print(response.text.encode('utf8'))

with open(in_filename, 'r') as input_csv, open(out_filename, 'w') as out_csv:
    input_dictRead = csv.DictReader(input_csv)
    fieldnames = ['id', 'responseStatus', 'errors']
    dw = csv.DictWriter(out_csv, lineterminator='\n', fieldnames=fieldnames)
    dw.writeheader()
    i = 0

    for row in input_dictRead:
        i += 1
        print("Processing row %d ..." % i),
        parameters = row.copy()
        del parameters['\ufeffid']
        r = requests.put(baseurl + '/objects/documents/' + row['\ufeffid'], headers={'Authorization': sessionID},
                         data=parameters)
        jsonResponse = r.json()
        out_row = {}
        print(jsonResponse['responseStatus'])
        if jsonResponse['responseStatus'] == 'SUCCESS':
            out_row['responseStatus'] = '%s' % jsonResponse['responseStatus']
            out_row['id'] = '%s' % row['\ufeffid']
            out_row['errors'] = 'No Errors'
        else:
            out_row['responseStatus'] = '%s' % jsonResponse['responseStatus']
            out_row['id'] = '%s' % row['\ufeffid']
            out_row['errors'] = '%s' % jsonResponse['errors']
        dw.writerow(out_row)

print("Done.")