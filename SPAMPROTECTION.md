# Spam/Invasion Protection System

## About 
Spam/Bot prevention system allows community owners to protect their members from media messages which are not 
approved by the guilds staff members and are termed to be treated as spam. Owner set ups the landing channel 
for all new members, and specifies the message
user needs to react with "thumbs up" emoji in order to get verified. When user joins "Unverified" role is assigned 
which, upon appropriate reaction to message, is replaced by Verified. 

Important to know for system to function optimally is:
```text
1. Guild needs to be registered in the Spam/Invasion Prevention System
1. Role @everyone should have all rights removed
2. Channel Needs to be created and role Unverified assigned to the channel (This will allow only for newcomers to see
it till they verify themselves.
```

## How to register for service
```text
*service register spam
```
Note: System will create automatically required roles to function optimally

## Entry Point 
By executing command below you will receive all available commands to manage Spam/Invasion protection system
```text
*spam
```

## Set-Up procedure
After Guild has been registered into the system follow the steps bellow
```text
1. Setting the landing channel
*spam set_channel <#discord.TextChannel>

2. Setting the reaction message
*spam set_message <message_id>
```

## Turning on protection system 
```text
*spam on
```

## Turning off protection system 
```text
*spam off
```

Note: By turning the system off you will need to manually re-set roles on the channels. 

[Back to main page](README.md)
