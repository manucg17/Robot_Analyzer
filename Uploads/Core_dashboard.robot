*** Settings ***
Library    RequestsLibrary
Resource  Variables.robot 
Resource  ../../../../LIBRARY/EXECUTION/Authorization.robot
Suite Setup  Authorization Validate

** Test Cases **
TC_Core_155 : Create dashboard to the system
    [Documentation]  Verify that Create dashboard to the system
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_155 : Create dashboard to the system started\n\n
    header session
    ${dashboardPermissionDTOList_Dict}  Create Dictionary  actionType=VIEW  allowedEntityType=EntityType  allowedEntityReference=1
    ${dashboardPermissionDTOList}  Create List  ${dashboardPermissionDTOList_Dict}
    ${data}  Create Dictionary  id=0  name=user2  owner=owner name  description=description  jsonData=sample data  dashboardPermissionDTOList=${dashboardPermissionDTOList}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/dashboard/create  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Fetch device id and make it as global variable
    ${dashboard}  Get Value From Json  ${response.json()}  id
    ${dashboard_string}  Convert To String  ${dashboard[0]}
    ${dashboard_id}  Set Variable  ${dashboard_string}
    Log To Console  \n printing device id
    Log To Console  ${dashboard_id}
    Set Suite Variable  ${dashboard_id}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_155 : Get all maintenance list from the system.\n

TC_Core_157 : Get dashboard list from the system
    [Documentation]  Verify that Get dashboard list from the system
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_157 : Get dashboard list from the system started\n\n
    header session
    ${response}  Post On Session  mysession  /core/rest/v1/dashboard/get-all  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}    200
    Log To Console  \nSuccessfully verify the TC_USER_157 : Get dashboard list from the system\n

TC_Core_158 : Update dashboard to the system
    [Documentation]  Verify that Update dashboard to the system
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_158 : Update dashboard to the system started\n\n
    header session
    ${dashboardPermissionDTOList_Dict}  Create Dictionary  actionType=VIEW  allowedEntityType=EntityType  allowedEntityReference=1
    ${dashboardPermissionDTOList}  Create List  ${dashboardPermissionDTOList_Dict}
    ${data}  Create Dictionary  id=${dashboard_id}  name=user3  owner=owner name  description=description  jsonData=sample data  dashboardPermissionDTOList=${dashboardPermissionDTOList}
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/dashboard/edit/${dashboard_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}    200
    Log To Console  \nSuccessfully verify the TC_USER_158 : Update dashboard to the system\n

TC_Core_159 : Get dashboard details by id
    [Documentation]  Verify that Get dashboard details by id
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_159 : Get dashboard details by id started\n\n
    header session
    Log To Console  Make the GET request
    ${response}  GET On Session  mysession  /core/rest/v1/dashboard/get-by-id/${dashboard_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}    200
    Log To Console  \nSuccessfully verify the TC_Core_159 : Get dashboard details by id\n

TC_Core_156 : Delete dashboard from the system
    [Documentation]  Verify the Delete dashboard from the system
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_156 : Delete dashboard from the system. started\n\n
    header session
    Log To Console  Make the DELETE request
    ${response}  Delete On Session  mysession  /core/rest/v1/dashboard/delete/${dashboard_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    #validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    ${res_body}  Convert To String  ${response.content}
    Should Contain  ${res_body}  Deleted Successfully
    Log To Console  \n\nSuccessfully verify the testcase TC_Core_156 : Delete dashboard from the system.\n