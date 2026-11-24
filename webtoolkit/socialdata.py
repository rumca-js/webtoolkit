from dataclasses import asdict, dataclass, field


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

    def __len__(self) -> int:
        """Returns the number of populated metrics."""
        metrics = (
            self.thumbs_up,
            self.thumbs_down,
            self.view_count,
            self.rating,
            self.upvote_ratio,
            self.upvote_diff,
            self.upvote_view_ratio,
            self.stars,
            self.followers_count,
        )
        return sum(1 for m in metrics if m is not None)

    def to_dict(self) -> dict:
        """Returns a JSON-serializable dict representation."""
        return asdict(self)

    def set_sources(self, sources: list[SocialSourceResult]) -> "SocialData":
        self.sources = sources
        errors = [s.error for s in sources if not s.ok and s.error]
        self.errors = errors or None
        return self

    @classmethod
    def from_dict(cls, data: dict | None) -> "SocialData":
        if isinstance(data, cls):
            return data
        if not data or not isinstance(data, dict):
            return cls()

        sources = []
        raw_sources = data.get("sources")
        if isinstance(raw_sources, list):
            for s in raw_sources:
                if isinstance(s, dict):
                    sources.append(
                        SocialSourceResult(
                            name=s.get("name", ""),
                            ok=bool(s.get("ok", False)),
                            error=s.get("error"),
                        )
                    )
                elif isinstance(s, SocialSourceResult):
                    sources.append(s)

        instance = cls(
            thumbs_up=data.get("thumbs_up"),
            thumbs_down=data.get("thumbs_down"),
            view_count=data.get("view_count"),
            rating=data.get("rating"),
            upvote_ratio=data.get("upvote_ratio"),
            upvote_diff=data.get("upvote_diff"),
            upvote_view_ratio=data.get("upvote_view_ratio"),
            stars=data.get("stars"),
            followers_count=data.get("followers_count"),
        )
        if sources:
            instance.set_sources(sources)

        raw_errors = data.get("errors")
        if raw_errors and isinstance(raw_errors, list):
            if instance.errors:
                for err in raw_errors:
                    if err and err not in instance.errors:
                        instance.errors.append(err)
            else:
                instance.errors = [str(e) for e in raw_errors if e] or None

        return instance
