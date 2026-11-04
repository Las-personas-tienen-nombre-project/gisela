"""Validación semántica de rasgos en el formato explícito GISELA v1.3."""

try:
    from traits import TraitsError, compile_catalog, validate_assignments
except ModuleNotFoundError:
    # CLI histórico: verify_contracts.py se ejecuta desde gisela/contracts.
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from traits import TraitsError, compile_catalog, validate_assignments


class TraitsMixin:
    def _check_traits_package(self, package: dict) -> None:
        """Valida referencias autorales, capacidad y operaciones TRAITS."""
        catalog = self._traits_catalog(package)
        if catalog is None:
            self._check_missing_traits_catalog(package)
            return
        cards = {c["id"]: c for c in package["cards"]}
        for i, card in enumerate(package["cards"]):
            if card["kind"] in ("character", "object", "location"):
                self._traits_validate(
                    catalog,
                    (card["kind"], card.get("traits", [])),
                    f"/cards/{i}/traits",
                )
            if card["kind"] == "skill" and "passive_traits" in card:
                self._traits_validate(
                    catalog,
                    ("character", card["passive_traits"]),
                    f"/cards/{i}/passive_traits",
                )
            if card["kind"] == "effect" and "granted_traits" in card:
                self._traits_validate(
                    catalog,
                    ("character", card["granted_traits"]),
                    f"/cards/{i}/granted_traits",
                )
        for group, kind in (
            ("characters", "character"),
            ("objects", "object"),
            ("locations", "location"),
        ):
            for i, item in enumerate(package["initial_state"][group]):
                inherited = (
                    cards[item["card"]].get("traits", [])
                    if item["card"] in cards
                    else []
                )
                self._traits_validate(
                    catalog,
                    (kind, item.get("traits", inherited)),
                    f"/initial_state/{group}/{i}/traits",
                )
        for effect, path in self.all_operations(package):
            if (
                effect.get("op") in ("assign_trait", "remove_trait")
                and effect["trait"] not in catalog["traits"]
            ):
                self.report("UNKNOWN_TRAIT", path + "/trait", "Rasgo no declarado")

    def _traits_catalog(self, package: dict):
        """Compila una vez para validación y falla cerrado ante catálogos inválidos."""
        try:
            return compile_catalog(package["traits"]) if "traits" in package else None
        except (TraitsError, ValueError, TypeError) as exc:
            self.report("TRAITS_INVALID", "/traits", str(exc))
            return None

    def _traits_validate(self, catalog, target: tuple, path: str) -> None:
        """Valida el conjunto sin materializarlo."""
        kind, assigned = target
        try:
            if catalog is None and assigned:
                raise TraitsError("Rasgos sin catálogo")
            if catalog is not None:
                validate_assignments(catalog, kind, assigned)
        except TraitsError as exc:
            self.report("TRAITS_INVALID", path, str(exc))

    def _check_traits_snapshot(self, snapshot: dict, package: dict) -> None:
        """Nunca rehídrata desde carta al restaurar un estado confirmado."""
        catalog = self._traits_catalog(package)
        for group, kind in (
            ("characters", "character"),
            ("objects", "object"),
            ("locations", "location"),
        ):
            for i, item in enumerate(snapshot["world"][group]):
                path = f"/world/{group}/{i}/traits"
                if "traits" not in item:
                    self.report(
                        "TRAITS_MISSING", path, "Falta estado confirmado de rasgos"
                    )
                else:
                    self._traits_validate(catalog, (kind, item["traits"]), path)
                    if item["traits"] != sorted(item["traits"]):
                        self.report(
                            "TRAITS_NONCANONICAL",
                            path,
                            "El conjunto persistido debe estar ordenado",
                        )

    def _check_missing_traits_catalog(self, package):
        for index, card in enumerate(package["cards"]):
            for field in ("traits", "passive_traits", "granted_traits"):
                if card.get(field):
                    self.report(
                        "TRAITS_MISSING",
                        f"/cards/{index}/{field}",
                        "Rasgos sin catálogo TRAITS",
                    )
        for group in ("characters", "objects", "locations"):
            for i, item in enumerate(package["initial_state"][group]):
                if item.get("traits"):
                    self.report(
                        "TRAITS_MISSING",
                        f"/initial_state/{group}/{i}/traits",
                        "Rasgos sin catálogo TRAITS",
                    )
