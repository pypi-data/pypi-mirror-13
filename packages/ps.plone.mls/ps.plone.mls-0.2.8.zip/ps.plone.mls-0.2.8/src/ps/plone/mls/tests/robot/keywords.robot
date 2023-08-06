*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/server.robot
Resource  Selenium2Screenshots/keywords.robot

Variables  plone/app/testing/interfaces.py
Variables  ps/plone/mls/tests/variables.py

Resource  ${PSPLONEMLS_PLONE_SELECTORS}
Resource  ${PSPLONEMLS_DEFAULT_SELECTORS}


*** Keywords ***

Setup
    Setup Plone site  ps.plone.mls.testing.ACCEPTANCE_TESTING
    Import library  Remote  ${PLONE_URL}/RobotRemote

Teardown
    Teardown Plone Site


*** Variables ***

${FOLDER_ID}  a-folder
${DOCUMENT_ID}  a-document
