## Database Considerations
### channel

Similar to a category, a channel is a container of topics and responses.

Channels can be created by any authenticated user in the system. The user that created the channel becomes the _owner_ of the channel (effectively an administrator) and allows them to manage certain aspects of it:

* Grant/Revoke administrative rights to other users (even if user is not subscribed to the channel.)
* Manage the channel's topics and responses, including editing them, mark a topic 'read only', and promoting them.

A channel can be public, or private. Public channels are available for reading to either anonymous users, or authenticated users (or both). Public channels can be made "writable" to Authenticated users.

Private channels are only available to the channel owner, other channel administrators, system administrators, and subscribed authenticated users, all the above profiles can read/write topics and comments, administrators can perform managerial tasks on the topics/comments as defined above.

**Channel Tag**. Channels must have a _tag_, or identifier (e.g. "py4web") and will be unique among channels, in order for the HTTP routing system to use a form similar to `[url]/channel/py4web`, or just `[url]/c/py4web`.

### topic
Topics will always be dependent on channels, topics can be locked (readonly) by the admins, and are editable by both admins and by their owner

