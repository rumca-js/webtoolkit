# BUGS

## Pre-existing Known Bugs

1. **`test_get_entries__hackernews` in `tests/unit/test_rsspage.py`**
   - **Failure**: `AssertionError: None is not true` on `self.assertTrue(entries[0]["author"])`.
   - **Reason**: The Hacker News RSS feed structure does not supply a recognized `<author>` or `<dc:creator>` field parsed by the RSS reader, causing `author` to evaluate to `None`.
   - **Note in test**: Explicitly noted in test docstring: `"it is a known error in hacker news that it does not work correctly, because"`.

2. **`test_get_cleaned_link__stupid_google_link4` in `tests/unit/test_urllocation.py`**
   - **Failure**: `AssertionError: 'https://www.google.com/goto?url=CAESVQHrOzAVcZvSERtSf...' != 'https://www.redditstatus.com'`.
   - **Reason**: Google `/goto?url=...` links employ server-side redirects with encoded protobuf/token payloads that cannot be decoded client-side without executing the redirect request.
   - **Note in test**: Explicitly noted in test docstring: `"Note: it is server sided reidrect, we are unable to decode it"`.
