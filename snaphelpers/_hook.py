from typing import (
    Callable,
    List,
    NamedTuple,
)

from ._importlib import (
    entry_points,
    EntryPoint,
    EntryPoints,
)

HOOKS_ENTRY_POINT = "snaphelpers.hooks"


class Hook(NamedTuple):
    """A snap hook declared via ``entry_points``."""

    name: str
    project: str
    module: str
    import_name: str
    path: str
    exists: bool

    @classmethod
    def from_entry_point(
        cls, entry: EntryPoint, skip_load: bool = False
    ) -> "Hook":
        """Return a ``Hook`` from an ``EntryPoint``."""
        project = entry.dist.name if entry.dist else ""
        exists = True
        if not skip_load:
            try:
                entry.load()  # type: ignore[no-untyped-call]
            except ModuleNotFoundError:
                exists = False
        return cls(
            name=entry.name,
            project=project,
            module=entry.module,
            import_name=entry.attr.split(".")[0],
            path=entry.attr,
            exists=exists,
        )

    @property
    def location(self) -> str:
        """The hook location."""
        return f"{self.module}:{self.path}"

    def __str__(self) -> str:
        return f"{self.location} ({self.project})"


def get_hooks(
    entry_points: Callable[..., EntryPoints] = entry_points,
    module: str | None = None,
) -> List[Hook]:
    """Return registered snap hooks.

    Resources registred as ``snaphelpers.hooks`` in ``entry-points`` are loaded
    as hooks, based on their name.

    For example, in ``pyproject.toml``:

    .. code:: toml

       [project.entry-points."snaphelpers.hooks"]
       configure = "foo.bar:configure_hook"
       install = "foo.bar:install_hook"

    """
    e_points = (
        entry_points(group=HOOKS_ENTRY_POINT, module=module)
        if module
        else entry_points(group=HOOKS_ENTRY_POINT)
    )
    return [Hook.from_entry_point(entry_point) for entry_point in e_points]
