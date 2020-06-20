# Virtual Air Marshal

## About

Virtual Air Marshal is a multi Discord Management Bot with various integrated manual and automatic services and commands to manage community.
The bot is owned by Launch Pad Investments Discord Group offering wide variety of services for their members.

## Bot command
@Virtual Air Marshal#8238 

## General management commands

### Admin 
Entry command for administration subcommands. In order to make them accessible a admin or a needs to be initiated after bot command to access sub-levels.

#### Kick user/users

Kicks the user from community.

```text
@Virtual Air Marshal#8238 admin kick <@discord.User or Multiple users tagged> <reason=Optional parameter>
```

#### Ban user/users

Ban user/users from community and deletes messages for last 7 days.

```text
@Virtual Air Marshal#8238 admin ban <@discord.User or Multiple users tagged> <reason=Optional parameter>
```

### Role 

Role management on community

```text
@Virtual Air Marshal#8238 role
```
#### Remove role from user

Removes the discord Role from selected user

```text
@Virtual Air Marshal#8238 role remove <discord.Member> <discord.Role>
```

#### Add role to user

Removes the discord Role from selected user

```text
@Virtual Air Marshal#8238 role add <discord.Member> <discord.Role>
```

### Create 

Allowes to create channels and roles

```text
@Virtual Air Marshal#8238 create
```

#### Create a text channel

Creates a text channel with specific name and optiona lsubject

```text
@Virtual Air Marshal#8238 create text_channel <channel_name>
```

#### Create a voice channel

Creates a text channel with specific name and optiona lsubject

```text
@Virtual Air Marshal#8238 create voice_channel <channel_name>
```

## Services

### Jail Profanity System
What is it

Bot monitors every message for profanity words, and once identified it applied strike to the user. Once 3 strikes are achieved, user is automatically
stripped of all roles, and Jailed role is assigned which prevents user to write on channels. Privileges can be modified by the administrators of the community
to fit the needs. Once user get jailed, he/she receives the role for 5 minutes. Once jail time is served, bot will automatically restore the users state to 
pre-jail time. 

How to setup 

1. @Virtual Air Marshal#8238 service register jail --> This will automatically create as well "Jailed" role if it does not exist on the community.
2. @Virtual Air Marshal#8238 jail on --> Turns the service ON and starts to monitor user messages on public channels.

Other available commands

- @Virtual Air Marshal#8238 jail off --> Turns the Jail service OFF

- @Virtual Air Marshal#8238 jail unjail @discord.User --> Administrators can release user from the jail before time expires

- @Virtual Air Marshal#8238 jail punish @discord.User duration(minutes) --> Throw user manually to jail for N minutes

### Bot Invasion protection System
- What is it
- How to set up
- Other available commands