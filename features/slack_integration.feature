Feature: Slack integration

     As a chat engineer,
     I want to receive events from Slack
     in order to trigger commands

     As a chat engineer,
     I want to update Slack conversations
     in order to interact with conversation members


Scenario: where a user joins a Slack conversation
     When a user joins Slack conversation
     Then Slack posts a bot event "team_join"
      And Lambda function "FromSlack" receives the bot event "team_join"
      And an event "MemberhipFromSlack" is posted to the bus

Scenario: where a new message is received from a Slack conversation
     When a message is posted to Slack conversation
     Then Slack posts a bot event "message.channels"
      And Lambda function "FromSlack" receives the bot event "message.channels"
      And an event "MessageFromSlack" is posted to the bus

Scenario: where a pin notification is received from a Slack conversation
     When a pin is added to Slack conversation
     Then Slack posts a bot event "pin_added"
      And Lambda function "FromSlack" receives the bot event "pin_added"
      And an event "PinFromSlack" is posted to the bus

Scenario: where a reaction is received from a conversation item
     When a reaction is added to an item in Slack conversation
     Then Slack posts a bot event "reaction_added"
      And Lambda function "FromSlack" receives the bot event "reaction_added"
      And an event "ReactionFromSlack" is posted to the bus

Scenario: where a message is posted to a Slack conversation
     When an event "MessageToSlack" is posted to the bus
     Then Lambda function "ToSlack" handles the event "MessageToSlack"
      And Slack conversation is updated with API call "chat.postMessage"

Scenario: where a message is updated in a Slack conversation
     When an event "UpdateToSlack" is posted to the bus
     Then Lambda function "ToSlack" handles the event "UpdateToSlack"
      And Slack conversation is updated with API call "chat.update"

Scenario: where a file is uploaded to a Slack conversation
     When an event "UploadToSlack" is posted to the bus
     Then Lambda function "ToSlack" handles the event "UploadToSlack"
      And Slack conversation is updated with API call "files.upload"
