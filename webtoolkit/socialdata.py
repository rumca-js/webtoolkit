from dataclasses import dataclass, field


@dataclass
class SocialSourceResult:
    name: str
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

    def set_sources(self, sources: list[SocialSourceResult]) -> "SocialData":
        self.sources = sources
        errors = [s.error for s in sources if not s.ok and s.error]
        self.errors = errors or None
        return self
