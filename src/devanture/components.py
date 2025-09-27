"""Components."""
from typing import Callable

_current_app = None

def set_app(app) -> None:
    """Set the current FastAPI app instance once for component routing."""
    global _current_app
    if _current_app is not None:
        raise ValueError("App already set—call set_app only once.")
    _current_app = app


def get_endpoint_path(endpoint_fn) -> str | None:
    """Retrieve the path for a given endpoint function by inspecting app routes."""
    app = get_current_app()
    if not app:
        return None
    for route in app.routes:
        if hasattr(route, 'endpoint') and route.endpoint == endpoint_fn:
            return route.path
    return None

class Text:
    def __init__(self, tag: str, text: str):
        self.tag = tag
        self.text = text

    def __html__(self) -> str:
        return f"<{self.tag}>{self.text}</{self.tag}>"

tags = (
    "P",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "Strong",
    "Var",
    "Code",
)

for cls_name in tags:
    globals()[cls_name] = type(
        cls_name,
        (Text,),
        {
            "__init__": (
                lambda t: lambda self, text: Text.__init__(self, t, text))(cls_name.lower())
        }
    )

def get_endpoint_path(endpoint) -> str | None:
    """Retrieve the path for a given endpoint function by inspecting app routes."""
    for route in _current_app.routes:
        if hasattr(route, 'endpoint') and route.endpoint == endpoint:
            return route.path
    return None


class Table():
    def __init__(self, columns: list[str] = [], data: list[dict] = [], id: str | None = None):
        self.data = data
        self.columns = columns
        self.id = id

    def rows(self, data) -> str:
        rows = ""
        for row in data:
            cells = "".join(f"<td>{row[c]}</td>" for c in self.columns)
            rows += f"<tr>{cells}</tr>"
        return rows

    def __html__(self) -> str:
        return f"""
        <table id="{self.id}">
            <tr>{''.join(f'<th>{c}</th>' for c in self.columns)}</tr>
            {self.rows(self.data)}
        </table>
        """

    def html(self) -> str:
        return self.__html__()



class Input:
    def __init__(
        self,
        name: str,
        placeholder: str = "",
        type_: str = "text",
        get: str | None = None,
        trigger: str | None = None,
        target: str | Table = None,
        include: str | None = None,
        on: str | None = None,
        swap: str | None = None,
    ):
        self.name = name
        self.placeholder = placeholder
        self.type_ = type_
        self.get = get_endpoint_path(get)
        self.trigger = trigger
        self.target = f"#{target.id}"
        self.include = include
        self.on = on
        self.swap = swap

    def __html__(self) -> str:
        attrs = [
            f'name="{self.name}"',
            f'type="{self.type_}"',
            f'placeholder="{self.placeholder}"',
        ]
        if self.get:
            attrs.append(f'hx-get="{self.get}"')
        if self.trigger:
            attrs.append(f'hx-trigger="{self.trigger}"')
        if self.target:
            attrs.append(f'hx-target="{self.target}"')
        if self.include:
            attrs.append(f'hx-include="{self.include}"')
        if self.on:
            attrs.append(f'hx-on="{self.on}"')
        if self.swap:
            attrs.append(f'hx-swap="{self.swap}"')
        return f"<input {' '.join(attrs)}>"


class Page():
    def __init__(self, title: str, components: list):
        self.title = title
        self.components = components

    def __html__(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <script src="https://unpkg.com/htmx.org@1.9.10"></script>
        </head>
        <body>
            {"".join(c.__html__() for c in self.components)}
        </body>
        <script>
        </script>
        </html>
        """

def render(page: Page) -> str:
    return page.__html__()
