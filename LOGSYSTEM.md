
# Logger System

## About

## How to register for logger system

```text
^vam service register logging
```

## Setup guide

### Initial set-up
Head to one of guild channels where Virtual Air Marshal has access to and execute command
```text
^vam logger set_channel <#discord.TextChannel>
```
 This will set the channel where all logs will be relayed. 
 Note: Same command can be used as well to set new channel.

### Turning logger on
```text
^vam logger on
```
### Turning logger off
 ```text
^vam logger off
```

## Currently integrated loggers

### Role Activity
- [X] Guild role create
- [X] Guild role delete
- [X] Guild role update
- [ ] Guild emoji update

### Member Activity
- [X] Member joining Guild
- [X] Member leaving Guild
- [X] Member Banned
- [X] Member Unbanned
- [X] Member update
- [X] User update
- [ ] Member voice state update
- [X] Member joined group
- [X] Member leaving group

### Invitations
- [X] Invite created
- [X] Invite deleted

### Channel activity

- [X] On guild channel create (Voice, Text, Category)
- [X] On guild channel delete (Voice, Text, Category)
- [X] On guild channel update (voice, Text, Category)
- [ ] Webhook update 

### Message Activity
- [x] On message delete
- [X] On message edit
- [X] On message pin/unpin

[Back to main page](README.md)

