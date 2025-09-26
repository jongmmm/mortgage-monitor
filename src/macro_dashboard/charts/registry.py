"""Component registry for macro_dashboard.

Similar to mortgage_monitor but generalized to components (charts or tables).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Type


@dataclass
class ComponentMetadata:
    name: str
    title: str
    component_class: Type
    order: int = 100
    enabled: bool = True
    page: str = "Overview"
    page_order: int = 100


class ComponentRegistry:
    _components: Dict[str, ComponentMetadata] = {}

    @classmethod
    def register(cls, meta: ComponentMetadata) -> None:
        if meta.name in cls._components:
            raise ValueError(f"Component '{meta.name}' already registered")
        cls._components[meta.name] = meta

    @classmethod
    def get(cls, name: str) -> Optional[ComponentMetadata]:
        return cls._components.get(name)

    @classmethod
    def all(cls) -> List[ComponentMetadata]:
        return sorted([m for m in cls._components.values() if m.enabled], key=lambda m: m.order)

    @classmethod
    def by_page(cls) -> Dict[str, List[ComponentMetadata]]:
        pages: Dict[str, List[ComponentMetadata]] = {}
        for c in cls.all():
            pages.setdefault(c.page, []).append(c)
        for comps in pages.values():
            comps.sort(key=lambda m: m.order)
        return pages


def register_component(
    name: str,
    title: str,
    order: int = 100,
    enabled: bool = True,
    page: str = "Overview",
    page_order: int = 100,
):
    def decorator(cls: Type):
        meta = ComponentMetadata(
            name=name,
            title=title,
            component_class=cls,
            order=order,
            enabled=enabled,
            page=page,
            page_order=page_order,
        )
        ComponentRegistry.register(meta)
        return cls

    return decorator

