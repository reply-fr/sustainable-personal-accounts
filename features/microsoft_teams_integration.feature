Feature: Microsoft Teams integration

     As a chat engineer,
     I want to update Microsoft Teams channels
     in order to interact with conversation members


Scenario: where a message is posted to a Microsoft Teams webhook
    Given Lambda function "ToMicrosoftTeams" is listening from the event bus
     When an event "PostMicrosoftTeamsMessage" is posted to the bus
     Then Lambda function "ToMicrosoftTeams" handles the event "PostMicrosoftTeamsMessage"
      And mesage is posted to provided webhook

