Feature: Microsoft Teams integration

     As a chat engineer,
     I want to update Microsoft Teams channels
     in order to interact with conversation members


     Scenario: where a message is posted to a Microsoft Teams webhook
          Given an existing SPA system
          When an event "MessageToMicrosoftTeams" is posted to the bus
          Then Lambda function "ToMicrosoftTeams" handles the event "MessageToMicrosoftTeams"
          And message is posted to provided webhook

