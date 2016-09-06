# reddit-cyborg

Reddit Cyborg is a personal automation assistant running under my main account /u/captainmeta4. It is similar to AutoModerator in design.

Reddit Cyborg is my only bot that is not available for easy widespread usage. This decision is due to its ability to issue automated subreddit bans based on arbitrarily specified criteria. While I have a specific and necessary use for this feature, please remember that automated bans are usually poor form.

If you are interested in running a clone of Cyborg yourself, feel free to fork the project.

#Valid Arguments

Cyborg operates on custom-specified rules in a manner similar to AutoModerator. The following is a list of available keys.

Matching criteria:

* `type` - must be `"both"`, `"link submission"`, `"text submission"`, or `"comment"`. Defaults to `"both"`
* `subreddit` - must be a `[list, of, subreddits]`
* `author_name` - must be a `[list, of, usernames]`
* `body` - must be a `[list, of, words]`. Applies only to comments and text submissions
* `domain` - must be a `[list.of, domai.ns]`. Applies only to link submissions
* `body_regex` - must be a regular expression.

Outputs:

* `action` - **must be a list** containing at least one of `remove`, `remove_parent`, `spam`, `spam_parent`, `ban`, `ban_parent`, `report`, `report_parent`, `approve`, `approve_parent`, `rts`, or `rts_parent`.
* `comment` - Comment to reply with. Comments are distinguished.
* `ban_duration` - Length of ban. Defaults to `None`.
* `ban_message` - Message given in ban notice. Defaults to nothing.
* `reason` - Action reason seen in mod log, ban notes, or report reason.
