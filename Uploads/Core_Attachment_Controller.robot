*** Settings ***
Library    RequestsLibrary
Resource  Variables.robot
Resource  ../../../../LIBRARY/EXECUTION/Authorization.robot
Suite Setup  Authorization Validate


*** Test Cases ***

TC_Core_378 : Add attachment to the system.
    [Documentation]  Verify that Add attachment to the system.
    [Tags]  TC_Core_378
    Log To Console  \n\n Testcase TC_Core_188 : Add attachment to the system.\n\n
    header session
    ${data}  Create Dictionary  id=0  filePath=/path  originalFileName=File  fileSizeInBytes=0  description=Attachment Description  createdAt=2024-03-06T05:30:37.359Z  updatedAt=2024-03-06T05:30:37.359Z  createdBy=0  updatedBy=0  parentModule=INCIDENT  moduleReferenceId=0
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/attachment/add  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Fetch attachment_file id and make it as global variable
    ${attachment_file}  Get Value From Json  ${response.json()}  id
    ${attachment_file_string}  Convert To String  ${attachment_file[0]}
    ${attachment_file_id}  Set Variable  ${attachment_file_string}
    Log To Console  \n printing device id
    Log To Console  ${attachment_file_id}
    Set Suite Variable  ${attachment_file_id}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_378 : Add attachment to the system.\n

TC_Core_377 : Get attachment from the system by filtering
    [Documentation]  Verify the Get attachment from the system by filtering
    [Tags]  TC_Core_377
    Log To Console  \n\n Testcase TC_Core_377 : Get attachment from the system by filtering started\n\n
    header session
    ${value}  Create List
    ${value_dict}  Create Dictionary  key=id  op=0  value=${value}
    ${data}  Create List  ${value_dict}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/attachment/get-all  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_377 : Get attachment from the system by filtering\n

TC_Core_378 : Add attachment to the system.
    [Documentation]  Verify that Add attachment to the system.
    [Tags]  TC_Core_378
    Log To Console  \n\n Testcase TC_Core_188 : Add attachment to the system.\n\n
    header session
    ${data}  Create Dictionary  id=${attachment_file_id}  filePath=/path  originalFileName=File  fileSizeInBytes=0  description=Attachment Description  createdAt=2024-03-06T05:30:37.359Z  updatedAt=2024-03-06T05:30:37.359Z  createdBy=0  updatedBy=0  parentModule=INCIDENT  moduleReferenceId=0
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/attachment/edit/${attachment_file_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_378 : Add attachment to the system.\n

TC_Core_379 : Retrieve attachment by id from system
    [Documentation]  Verify that Retrieve attachment by id from system
    [Tags]  TC_Core_379
    Log To Console  \n\n Testcase TC_Core_379 : Retrieve attachment by id from system started\n\n
    header session
    Log To Console  Make the GET request
    ${response}  GET On Session  mysession  /core/rest/v1/attachment/get/${attachment_file_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}    200
    Log To Console  \nSuccessfully verify the TC_Core_379 : Retrieve attachment by id from system\n

TC_Core_381 : Delete attachment from system
    [Documentation]  Verify the Delete attachment from system
    [Tags]  TC_Core_381
    Log To Console  \n\n Testcase TC_Core_381 : Delete attachment from system\n\n
    header session
    Log To Console  Make the DELETE request
    ${response}  Delete On Session  mysession  /core/rest/v1/attachment/delete/${attachment_file_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    #validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \n\nSuccessfully verify the testcase TC_Core_381 : Delete attachment from system\n

TC_Core_382 : Delete file.
    [Documentation]  Verify the Delete file.
    [Tags]  TC_Core_382
    Log To Console  \n\n Testcase TC_Core_382 : Delete file.\n\n
    header session
    Log To Console  Make the DELETE request
    ${response}  Delete On Session  mysession  /core/rest/v1/attachment/delete-file/${attachment_file_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    #validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    ${res_body}  Convert To String  ${response.content}
    Should Contain  ${res_body}  deleted successfully
    Log To Console  \n\nSuccessfully verify the testcase TC_Core_382 : Delete file..\n