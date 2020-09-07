# Administration Commands

## About
This part of the bot provides various administrative commands which community members
with sufficienty privileges can utilize for moderation. Owner of the guild
has access to all of the below presented commands, while others require certain permissions. All commands need to be 
executed on public channel of the cocmmunity.

## Entry Point

```text
^vam admin
```

## Member Management

### Kick Member
In order to be able to kick the member from guild you need to have higher ranked guild role
```text
One of two permissions required:
# Administrator Permission
# Kick Members Permission
```

```text
^vam admin kick <@discord.Member or multi> <reason = Optional>
```

### Ban Member
In order to be able to ban the member from guild you need to have higher ranked guild role
```text
One of two permissions required:
# Administrator Permission
# Ban Members Permission
```

```text
^vam admin ban <@discord.Member or multi> <reason = Optional>
```

### Add Role to Member
In order to be able to ban the member from guild you need to have higher ranked guild role
```text
One of two permissions required:
# Administrator Permission
# Manage Role Permissions
```

```text
^vam admin role add <@discord.Member > <@discord.Role>
```

### Remove role from Member
In order to be able to ban the member from guild you need to have higher ranked guild role
```text
One of two permissions required:
# Administrator Permission
# Manage Role Permissions
```

```text
^vam admin role remove <@discord.Member > <@discord.Role>
```

## Create from bot
This set of sub commands allows to create channels, roles, etc.

Entry point is 

```text
^vam admin create
```

### Create Text Channel

```text
One of two permissions required:
# Guild owner
# Administrator Permission
```

```text
^vam admin create text_channel <channel name = None>  

# If no channel name provided that channel name NewChannel will used
```

### Create Voice Channel

```text
One of two permissions required:
# Guild owner
# Administrator Permission
```

```text
^vam admin create text_channel <channel name = None>  

# If no channel name provided that channel name NewVoice will used
```

## Feature request

If you would like to have some other commands, please contact us through 

```text
^vam sys feature <message>
```
and we will put your request to development road if doable.

[Back to main page](README.md)
