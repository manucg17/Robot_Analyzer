*** Settings ***

Resource  Core_Keywords.resource  # Import the keyword file
Library    RequestsLibrary
Resource  Variables.robot
Suite Setup  Token Generation    # Call the Token Generation keyword

*** Test Cases ***

###################################################### Incident State #####################################################

TC_Core_183 : Retrieve incident state from the system by filtering.
    [Documentation]  Verify the Retrieve incident state from the system by filtering.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_183 : Retrieve incident state from the system by filtering.\n\n
    header session
    ${value}  Create List
    ${value_dict}  Create Dictionary  key=id  op=0  value=${value}
    ${data}  Create List  ${value_dict}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/incident-state/get-all  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_183 : Retrieve incident state from the system by filtering.\n

TC_Core_184 : Retrieve the incident state from the system.
    [Documentation]  Verify that Retrieve the incident state from the system.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_184 : Retrieve the incident state from the system.\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident-state/get/99951    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_184 : Retrieve the incident state from the system.\n

# Incident

TC_Core_160 : Create an Incident.
    [Documentation]  Verify that Create an Incident.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_160 : Create an Incident started\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalatedTo}  Create Dictionary  id=0
    ${assignee}  Create Dictionary  id=100042
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${escalatedTo}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${data}  Create Dictionary  id=0  uniqueId=0  title=Title for the incident occurred  description=description  priority=1  severity=1  incidentState=${incidentState}  assigneeType=USER  assignee=${assignee}  createdAt=${None}  createdBy=0  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/incident/add  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Fetch incident id and make it as global variable
    ${incident}  Get Value From Json  ${response.json()}  id
    ${incident_string}  Convert To String  ${incident[0]}
    ${incident_id}  Set Variable  ${incident_string}
    Log To Console  \n printing incident id
    Log To Console  ${incident_id}
    Set Suite Variable  ${incident_id}
    # Fetch Created date
    ${incident_create}  Get Value From Json  ${response.json()}  createdAt
    ${incident_create_string}  Convert To String  ${incident_create[0]}
    ${incident_create_date}  Set Variable  ${incident_create_string}
    Log To Console  \n printing incident created date
    Log To Console  ${incident_create_date}
    Set Suite Variable  ${incident_create_date}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_160 : Create an Incident\n

TC_Core_162 : Update incident to the system
    [Documentation]  Verify that Update incident to the system
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_162 : Update incident to the system\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalatedTo}  Create Dictionary  id=0
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${escalatedTo}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${data}  Create Dictionary  id=0  uniqueId=0  title=Edit incident  description=description  priority=1  severity=1  incidentState=${incidentState}  createdAt=${None}  createdBy=0  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/incident/edit/${incident_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_162 : Update incident to the system\n
#
TC_Core_168 : Set Escalation Configuration.
    [Documentation]  Verify that Set Escalation Configuration
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_168 : Set Escalation Configuration.\n\n
    header session
    ${id}  Create Dictionary  id=0
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${id}
    ${data}  Create List  ${escalationConfiguration_dict}
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/incident/set-escalation-configuration/${incident_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_168 : Set Escalation Configuration\n

TC_Core_163 : Assign the received incident to an individual for resolving.
    [Documentation]  Verify that Assign the received incident to an individual for resolving.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_163 : Assign the received incident to an individual for resolving.\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${assignee}  Create Dictionary  id=100042
    ${primaryAssignee}  Create Dictionary  id=99951
    ${id}  Create Dictionary  id=0
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${id}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${data}  Create Dictionary  id=0  uniqueId=0  title=Title for the incident occurred  description=description  priority=1  severity=1  incidentState=${incidentState}  assigneeType=USER  assignee=${assignee}  primaryAssignee=${primaryAssignee}  createdAt=${incident_create_date}  createdBy=0  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/incident/assign/${incident_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_163 : Assign the received incident to an individual for resolving.\n

TC_Core_164 : Get all incident list from the system.
    [Documentation]  Verify the Get all incident list from the system.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_164 : Get all incident list from the system started\n\n
    header session
    ${value}  Create List
    ${value_dict}  Create Dictionary  key=id  op=0  value=${value}
    ${data}  Create List  ${value_dict}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/incident/get-all  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_164 : Get all incident list from the system.\n

TC_Core_165 : Verify that Resolve the received incident
    [Documentation]  Verify that Resolve the received incident
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_165 : Resolve the received incident\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${id}  Create Dictionary  id=0
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${id}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${data}  Create Dictionary  id=0  uniqueId=0  title=Title for the incident occurred  description=description  priority=1  severity=1  incidentState=${incidentState}  assigneeType=USER  createdAt=${incident_create_date}  createdBy=0  resolvedBy=${id}  resolvedAt=${None}  resolutionNotes=Resolution Notes after the incident is resolved  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/incident/resolve/${incident_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Fetch Resolve date
    ${incident_resolve}  Get Value From Json  ${response.json()}  resolvedAt
    ${incident_resolve_string}  Convert To String  ${incident_resolve[0]}
    ${incident_resolve_date}  Set Variable  ${incident_resolve_string}
    Log To Console  \n printing incident resolve date
    Log To Console  ${incident_resolve_date}
    Set Suite Variable  ${incident_resolve_date}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_165 : Resolve the received incident\n

TC_Core_166 : Verify that the incident is resolved.
    [Documentation]  Verify that the incident is resolved.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_166 : Verify that the incident is resolved.\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${id}  Create Dictionary  id=0
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${id}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${data}  Create Dictionary  id=0  uniqueId=0  title=Title for the incident occurred  description=description  priority=1  severity=1  incidentState=${incidentState}  assigneeType=USER  createdAt=${incident_create_date}  createdBy=0  resolvedBy=${id}  resolvedAt=${incident_resolve_date}  resolutionNotes=Resolution Notes after the incident is resolved    verifiedBy=${id}  verifiedAt=${None}  verificationNotes=Verification notes after the incident is verified  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/incident/verify/${incident_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Fetch Verify date
    ${incident_verified}  Get Value From Json  ${response.json()}  verifiedAt
    ${incident_verified_string}  Convert To String  ${incident_verified[0]}
    ${incident_verified_date}  Set Variable  ${incident_verified_string}
    Log To Console  \n printing incident resolve date
    Log To Console  ${incident_verified_date}
    Set Suite Variable  ${incident_verified_date}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_166 : Verify that the incident is resolved.\n

TC_Core_167 : Close the resolved incident.
    [Documentation]  Verify that Close the resolved incident.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_167 : Close the resolved incident.\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${id}  Create Dictionary  id=0
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${id}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${data}  Create Dictionary  id=0  uniqueId=0  title=Title for the incident occurred  description=description  priority=1  severity=1  incidentState=${incidentState}  assigneeType=USER  createdAt=${incident_create_date}  createdBy=0  resolvedBy=${id}  resolvedAt=${incident_resolve_date}  resolutionNotes=Resolution Notes after the incident is resolved    verifiedBy=${id}  verifiedAt=${incident_verified_date}  verificationNotes=Verification notes after the incident is verified  closedBy=${id}  closedAt=${None}  closureNotes=Closure Notes after the incident is closed  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    Log To Console  Make the PUT request
    ${response}  Put On Session  mysession  /core/rest/v1/incident/close/${incident_id}  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Fetch Close date
    ${incident_closed}  Get Value From Json  ${response.json()}  closedAt
    ${incident_closed_string}  Convert To String  ${incident_closed[0]}
    ${incident_closed_date}  Set Variable  ${incident_closed_string}
    Log To Console  \n printing incident resolve date
    Log To Console  ${incident_closed_date}
    Set Suite Variable  ${incident_closed_date}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_167 : Close the resolved incident.\n

TC_Core_169 : Get open incidents count by primary assignee id
    [Documentation]  Verify thatGet open incidents count by primary assignee id
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_169 : Get open incidents count by primary assignee id\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-open-incident-count-by-primary-assignee-id    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_169 : Get open incidents count by primary assignee id\n

TC_Core_170 : Get all incident summary
    [Documentation]  Verify that Get all incident summary
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_170 : Get all incident summary\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-incident-summary    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_170 : Get all incident summary\n

TC_Core_171 : Get list of incidents based on incident severity
    [Documentation]  Verify that Get list of incidents based on incident severity
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_171 : Get list of incidents based on incident severity\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-incident-severity    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_171 : Get list of incidents based on incident severity\n

TC_Core_172 : Get incident responsible entity type metadata
    [Documentation]  Verify that Get incident responsible entity type metadata
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_172 : Get incident responsible entity type metadata\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-incident-responsible-entity-type    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_172 : Get incident responsible entity type metadata\n

TC_Core_173 : Get list of incidents based on incident priority
    [Documentation]  Verify that Get list of incidents based on incident priority
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_173 : Get list of incidents based on incident priority\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-incident-priority    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_173 : Get list of incidents based on incident priority\n

TC_Core_174 : Get count of SLA breached incidents
    [Documentation]  Verify that Get count of SLA breached incidents
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_174 : Get count of SLA breached incidents\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-count-of-sla-breached-incident    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_174 : Get count of SLA breached incidents\n

TC_Core_175 : Get incident details by id.
    [Documentation]  Verify that Get incident details by id.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_175 : Get incident details by id.\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-by-id/${incident_id}    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_175 : Get incident details by id.\n

TC_Core_176 : Get average resolution time of the account
    [Documentation]  Verify that Get average resolution time of the account
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_176 : Get average resolution time of the account\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-average-resolution-time    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_176 : Get average resolution time of the account\n

TC_Core_177 : Get all SLA configuration by incident id.
    [Documentation]  Verify that Get all SLA configuration by incident id.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_177 : Get all SLA configuration by incident id.\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-all-sla-configurations-by-incident-id/${incident_id}    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_177 : Get all SLA configuration by incident id.\n

TC_Core_178 : Get all open incident count.
    [Documentation]  Verify that Get all open incident count.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_178 : Get all open incident count.\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-all-open-incident-count    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_178 : Get all open incident count.\n

TC_Core_179 : Get all incident count
    [Documentation]  Verify that Get all incident count
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_179 : Get all incident count\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-all-incident-count    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_179 : Get all incident count\n

TC_Core_180 : Get all incident count by state
    [Documentation]  Verify thatGet all incident count by state
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_180 : Get all incident count by state\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-all-incident-count-by-state    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_180 : Get all incident count by state\n

TC_Core_181 : Get all incident count by severity
    [Documentation]  Verify that Get all incident count by severity
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_181 : Get all incident count by severity\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-all-incident-count-by-severity    headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_181 : Get all incident count by severity\n

TC_Core_182 : Get all incident count by priority
    [Documentation]  Verify that Get all incident count by priority
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_182 : Get all incident count by priority\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident/get-all-incident-count-by-priority  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_182 : Get all incident count by priority\n

################################################### Incident history ####################################################
TC_Core_185 : Create an incident history.
    [Documentation]  Verify that Create an incident history.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_185 : Create an incident history.\n\n
    header session
    ${incidentState}  Create Dictionary  id=99952  stateOrder=2  name=Assigned  description=description  defaultIncidentState=${None}
    ${id}  Create Dictionary  id=0
    ${customSLAConfiguration_dict}  Create Dictionary  id=0  incidentPriority=1  escalationLevel=1  escalationThresholdInMinutes=5  sendSms=true  sendEmail=true
    ${customSLAConfiguration}  Create List   ${customSLAConfiguration_dict}
    ${escalationConfiguration_dict}  Create Dictionary  escalationLevel=1  escalationType=USER  escalatedTo=${id}
    ${escalationConfiguration}  Create List  ${escalationConfiguration_dict}
    ${incidentDTO}  Create Dictionary  id=${incident_id}  uniqueId=0  title=Title for the incident occurred  description=description  priority=1  severity=1  incidentState=${incidentState}  assigneeType=USER  assignee=${id}  primaryAssignee=${id}  createdAt=${incident_create_date}  createdBy=0  resolvedBy=${id}  resolvedAt=${incident_resolve_date}  resolutionNotes=Resolution Notes after the incident is resolved    verifiedBy=${id}  verifiedAt=${incident_verified_date}  verificationNotes=Verification notes after the incident is verified  closedBy=${id}  closedAt=${incident_closed_date}  closureNotes=Closure Notes after the incident is closed  customSLA=true  customSLAConfiguration=${customSLAConfiguration}  escalationConfiguration=${escalationConfiguration}
    ${geoTag}  Create Dictionary  latitude=0  longitude=0  address=address
    ${data}  Create Dictionary  id=0  incidentDTO=${incidentDTO}  incidentActionType=CREATED  actionDescription=Incident Created  primaryAssigneeId=0  incidentState=NEW  performedAt=2024-03-04T07:54:19.291Z  performedBy=0  details=Incident action details  geoTag=${geoTag}  geoTagTimeStamp=2024-03-04T07:54:19.291Z
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/incident-history/add  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_185 : Create an incident history.\n

TC_Core_186 : Get all incident history list from the system.
    [Documentation]  Verify the Get all incident history list from the system.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_186 : Get all incident history list from the system.\n\n
    header session
    ${value}  Create List
    ${value_dict}  Create Dictionary  key=id  op=0  value=${value}
    ${data}  Create List  ${value_dict}
    Log To Console  Make the POST request
    ${response}  Post On Session  mysession  /core/rest/v1/incident-history/get-all  json=${data}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_186 : Get all incident history list from the system.\n

TC_Core_187 : Get incident history details by incident id.
    [Documentation]  Verify that Get incident history details by incident id.
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_187 : Get incident history details by incident id.\n\n
    header session
    Log To Console  Make the GET request
    ${response}  Get On Session  mysession  /core/rest/v1/incident-history/get-by-incident-id/${incident_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    # Validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    Log To Console  \nSuccessfully verify the TC_Core_187 : Get incident history details by incident id.\n

################################################### Incident notification ################################################

###########################################################################################################################

TC_Core_161 : Delete incident from the system
    [Documentation]  Verify the Delete incident from the system
    [Tags]  API testing
    Log To Console  \n\n Testcase TC_Core_161 : Delete incident from the system started\n\n
    header session
    Log To Console  Make the DELETE request
    ${response}  Delete On Session  mysession  /core/rest/v1/incident/delete/${incident_id}  headers=${header}
    Log To Console  \n Printing Response code and Response Content\n
    Log To Console  ${response.status_code}
    Log To Console  ${response.content}
    #validating the output
    ${status_code}  Convert To String  ${response.status_code}
    Should Be Equal  ${status_code}  200
    ${res_body}  Convert To String  ${response.content}
    Should Contain  ${res_body}  Deleted Successfully
    Log To Console  \n\nSuccessfully verify the testcase TC_Core_161 : Delete incident from the system.\n