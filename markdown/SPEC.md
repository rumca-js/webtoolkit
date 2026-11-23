# Feature Specification: Social Data Error Reporting

## 1. Problem Statement & Scope

Problem: get_social_data() returns a plain dict with no way to signal why a field
is missing — network failure, unsupported platform, rate limit, parse error. Callers
cannot distinguish "not supported" from "fetch failed", and when a handler queries
multiple sources or an external API fails, failures are either silently swallowed or
drop data without error diagnostics.

In Scope:
- New module `webtoolkit/socialdata.py` with `SocialData` and `SocialSourceResult` dataclasses
- Update `ContentInterface.get_social_data()` return type annotation to `SocialData`
- Update `HandlerInterface.get_social_data()` to return `SocialData` populated from getter methods
- Update `HandlerVideoYoutube.get_social_data()` with per-source tracking (Return Dislike API)
- Update `RedditUrlHandler.get_social_data()` with per-source tracking (`reddit_json`)
- Update `GitHubUrlHandler.get_social_data()` with per-source tracking (`github_api`)
- Update `HackerNewsHandler.get_social_data()` with per-source tracking (`hackernews_api`)
- Update `ReturnDislike.get_social_data()` with per-source tracking (`return_dislike`)
- Unit test coverage for all updated handlers and `SocialData` error scenarios
- Export `SocialData` and `SocialSourceResult` from `webtoolkit/__init__.py`

Out of Scope:
- RemoteUrl / RemoteServer social data path (separate ticket, depends on get_socialj cleanup)
- Per-field granularity (each field carrying its own status)
- Persistent error logging or alerting infrastructure beyond `WebLogger.error`
- Channel handlers without social endpoints (they inherit no-op / getter defaults)


## 2. User Stories & Acceptance Criteria

US-1: As a consumer of BaseUrl, I want get_social_data() to tell me whether the fetch
      succeeded across all social handlers so I can surface meaningful error messages.
  - [ ] Calling get_social_data() on any supported social handler returns a `SocialData`
        instance with attribute access, not a plain dict
  - [ ] When an API fetch fails (non-200, invalid JSON, exception), `sources` contains
        a `SocialSourceResult` with `ok=False` and a non-empty `error` string
  - [ ] When all queried sources fail, `errors` is a non-empty list of error strings
  - [ ] When all queried sources succeed, `errors` is None

US-2: As a handler author, I want a consistent return type contract across the handler hierarchy.
  - [ ] `ContentInterface.get_social_data()` carries a return type annotation of `SocialData`
  - [ ] `HandlerInterface.get_social_data()` returns `SocialData` mapping available getter values
        (`get_thumbs_up()`, `get_user_stars()`, `get_upvote_diff()`, etc.)
  - [ ] Handlers with no social properties return `SocialData` with all fields None,
        empty `sources`, and `errors=None`


## 3. Data & Schema Changes

New types in `webtoolkit/socialdata.py`:

```python
from dataclasses import dataclass, field

@dataclass
class SocialSourceResult:
    name: str          # e.g. "return_dislike", "reddit_json", "github_api", "hackernews_api"
    ok: bool
    error: str | None = None

@dataclass
class SocialData:
    thumbs_up: int | None = None
    thumbs_down: int | None = None
    view_count: int | None = None
    rating: float | None = None
    upvote_ratio: float | None = None
    upvote_diff: int | None = None
    upvote_view_ratio: float | None = None
    stars: float | None = None
    followers_count: int | None = None
    errors: list[str] | None = None
    sources: list[SocialSourceResult] = field(default_factory=list)
```

Field notes:
- `errors` is None when all sources succeeded (or there were no sources). It becomes a
  list of strings as soon as any source fails.
- `sources` is a list of `SocialSourceResult` objects tracking each attempted source.
- All numeric/ratio fields remain typed as `int | None` or `float | None`.


## 4. API & Endpoint Contracts

No HTTP endpoints are introduced or changed.

Public Python API changes:

```python
# Before
handler.get_social_data() -> dict

# After
handler.get_social_data() -> SocialData

# BaseUrl (unchanged call site, return type changes)
base_url.get_social_properties() -> SocialData
```

Backward compatibility:
- Dict indexing (`result["thumbs_up"]`) is deprecated/broken in favor of attribute access (`result.thumbs_up`).


## 5. Architecture & Flow

### HandlerInterface.get_social_data():
```python
def get_social_data(self) -> SocialData:
    return SocialData(
        thumbs_up=self.get_thumbs_up(),
        thumbs_down=self.get_thumbs_down(),
        view_count=self.get_view_count(),
        rating=self.get_rating(),
        upvote_ratio=self.get_upvote_ratio(),
        upvote_diff=self.get_upvote_diff(),
        upvote_view_ratio=self.get_upvote_view_ratio(),
        stars=self.get_user_stars(),
        followers_count=self.get_followers_count(),
    )
```

### HandlerVideoYoutube.get_social_data():
Queries Return Dislike API, creates `SocialSourceResult(name="return_dislike", ...)`, logs on error, and populates `SocialData`.

### RedditUrlHandler.get_social_data():
Queries `self.get_json_text()`. If retrieval or parsing fails, logs with `WebLogger.error` and records `SocialSourceResult(name="reddit_json", ok=False, error=...)`. When successful, populates `upvote_ratio`, `rating`, or `followers_count` and records `SocialSourceResult(name="reddit_json", ok=True)`.

### GitHubUrlHandler.get_social_data():
Queries `self.get_json_object()`. If missing or invalid, logs with `WebLogger.error` and records `SocialSourceResult(name="github_api", ok=False, error=...)`. When successful, populates `stars` and records `SocialSourceResult(name="github_api", ok=True)`.

### HackerNewsHandler.get_social_data():
Queries `self.get_json_object()`. If missing or invalid, logs with `WebLogger.error` and records `SocialSourceResult(name="hackernews_api", ok=False, error=...)`. When successful, populates `upvote_diff` and records `SocialSourceResult(name="hackernews_api", ok=True)`.

### ReturnDislike.get_social_data():
Queries `self.load_response()`. If missing or invalid, logs with `WebLogger.error` and records `SocialSourceResult(name="return_dislike", ok=False, error=...)`. When successful, populates `thumbs_up`, `thumbs_down`, `view_count`, `rating` and records `SocialSourceResult(name="return_dislike", ok=True)`.


## 6. Edge Cases & Failure Modes

- Remote source HTTP non-200 or invalid payload: `SocialSourceResult.ok=False`, `error` contains description, `SocialData.errors` contains the message.
- Network exception raised during request: caught in `try...except`, logged via `WebLogger.error`, recorded as failed source.
- Handler has no social metrics supported: all fields None, `sources=[]`, `errors=None`.
- Partial failure: successful source populates its fields; failed source sets `errors` and `ok=False` on its `SocialSourceResult`.


## 7. Security & Observability

- Read-only fetches of public endpoints.
- Errors logged via `WebLogger.error(...)`.
- Structured `SocialData.errors` and `SocialData.sources` provide direct diagnostics to callers.
