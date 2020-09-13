# Jail System

## About
Jail system provides Guild owners and administrators with unique opportunity to send their members on "cooldown" instead
kick or banning them. Once discord member is jailed, he/she will automatically receive ***Jailed*** role, and bee 
"stripped" of all the other roles. Their state will be restored once Jail Time Expires automatically, by the Virtual
Air Marshal.

## Required permissions
Guild needs to be registered in Virtual Air Marshal Jail system

### Bot's mandatory permission
```text
1. administrator
2. manage message
3. manage_roles
```
### Member has to have one of the following permissions
```text
- administrator
- community owner
```
## Role: ***Jailed**
Role is given to all users who are jailed, and taken away once jail time expires. It is the responsibility of the 
guild owner or administrator to set-up what "privileges" guild wide, rights, and access to channels jailed members
will have. 

## Entry Point to operate with Jail

By executing command below you will receive all available commands to manage Spam/Invasion protection system
```text
^vam jail
```

## How to register for jail service
Once below command is execute guild will be registered into jail system and new role on community called ***Jailed*** 
created. 

!Important! 
Discord roles are organized based on ranking. If role is positioned lower than the highest role of member who is getting
jailed there is a chance that jail command will not be working. 

Users higher in role ranking can not be jailed by the members of the lower rank.

### Initial registration of guild into system
```text
^vam service register jail
```

### Turn the Jail ON

```text
^vam jail on
```

### Turn the Jail OFF

```text
^vam jail off
```

## How to jail and un-jail members
System is designed so, that it automatically releases users from the jail once set sentece time exires.

### Jail Member for N minutes
```text
^vam punish <duration in minutes = Integer> <Reason for jail= Optional>
```
Once member is successfully jailed, he will be "stripped" of all the roles he has had up till being jailed and 
assigned role ***Jailed***. System will store all roles and re-assign them once jail time expires.

### Un-jail Member who is jailed

```text
^vam release <@discord.Member> 
```
Upon successful release, Virtual Air Marshal will automatically return user all roles from the "pre-jail time".

[Back to main page](README.md)

