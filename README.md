# gitbucket-servicehook-injector
Set up a service hook in the GitBucket repository

## Requirement
+ Python2.7 or 3.x

## Supprted OS
+ Windows
+ `*nix`

## Installation
```sh
$ pip install -U git+https://github.com/maskedw/gitbucket-servicehook-injector

```
## Usage
```
$ gitbucket-servicehook-injector -h
usage: gitbucket-servicehook-injector [-h] [--version] [--log LOG] [--beacon]
                                      [--dry-run] [-v]
                                      config_file

Set up a service hook in the GitBucket repository

positional arguments:
  config_file    Configuration File(YAML)

optional arguments:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  --log LOG      Log file path (default: )
  --beacon       Prints a message at startup (default: False)
  --dry-run      Perform a trial run with no changes made (default: False)
  -v, --verbose  Enable verbose output (default: False)
```

## Example

**Config Example**  

```yaml
admin_user:
  name: foo
  password: foo-password
feed_url: http://example.com/gitbucket/activities.atom
root_url: http://example.com/gitbucket
service_hooks:
- url: https://hooks.slack.com/services/XXXXXXXXXXX
  token: ''
  ctype: json
  events:
    issue_comment: 'on'
    issues: 'on'
    pull_request: 'on'
    pull_request_review_comment: 'on'
    push: 'on'
```

**Edit crontab**  

Allow polling at appropriate intervals.

```
*/1 * * * * user gitbucket-servicehook-injector --beacon --log=/home/user/gitbucket-servicehook-injector.log /home/user/gitbucket-servicehook-injector.yaml
```

