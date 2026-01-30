## Manual Procedures
### Required Modules

- markdown
- python-dotenv
- better_profanity
- faker

### Create User
### Make Non-Admin user Admin

In DB, find the Id of user to add to the manager group.
In  common.py -> groups = Tags(db.auth_user, "groups")
from .common import groups
groups.add(1, 'manager')

or -

In auth_user_tag_groups (table)
insert into auth_user_tag_groups values (null, 'manager', 1)

