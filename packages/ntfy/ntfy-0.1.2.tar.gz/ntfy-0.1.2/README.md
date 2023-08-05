# About `ntfy`

`ntfy` is a command line utility (and to a degree, python library) for sending
push notifications. It also can send a notification when a program finishes.

Unlike many existing utilities for Pushover or Pushbullet,
it supports multiple backends.

## Usage
```

# send a notification
ntfy send "Here's a notification!"

# send a notification with custom title (default is $USER@$HOST)
ntfy send -t 'ntfy' "Here's a notification with a custom title!"

# send a notification when the command `sleep 10` finishes
# this send the message '"sleep 10" succeeded in 0.2 minutes'
ntfy done sleep 10
```


# Backends
 - [x] [Pushover](https://pushover.net)
 - [x] [Pushbullet](https://pushbullet.com)
 - [x] Linux Desktop Notifications (notify-send)
 - [ ] [Prowl](http://www.prowlapp.com)
 - [ ] [Airgram](http://www.airgramapp.com)
 - [ ] [Pushjet](https://pushjet.io)
 - [ ] [Pushalot](https://pushalot.com)
 - [ ] [Boxcar](https://boxcar.io)
 - [ ] [Instapush](https://instapush.im)
 - [ ] Mac OS X Notification Center
 - [ ] Windows Desktop Notifications?

## Config
`ntfy` is configured via a json config file stored at `~/.ntfy.json`. It
requires at minimum 2 keys: backend & a config for that backend.

### Example Config
```
{
    "backend": "pushbullet",
    {"pushbullet": {"access_token": "<redacted>"}}
}
```
