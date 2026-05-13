"""Thin FastAPI router — delegates everything to use cases.

No business logic lives here. This is pure transport-layer glue.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from refactor.api.schemas import SuspensionRequest, AddOptionRequest
from refactor.api.dependencies import get_suspension_use_cases, get_options_use_cases

router = APIRouter()


# ── Suspension endpoints ──────────────────────────────────────

@router.post("/preview")
async def preview(body: SuspensionRequest) -> list[list[dict[str, str]]]:
    """Preview what would happen when suspending the listed IPs.

    Returns the same shape as the original API: [[comment_list], [comment_finally]].
    Each entry has {id, comment} — matching the pre-refactor contract.
    """
    try:
        uc = get_suspension_use_cases()
        result = await uc.preview(
            spreadsheet_name=body.SPREADSHEET_NAME,
            mikrotik_ip=body.IP_MIKROTIK,
            date=body.DATE,
        )
        return [
            [{"id": e.id, "comment": e.comment} for e in result.current_comments],
            [{"id": e.id, "comment": e.comment} for e in result.final_comments],
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/script")
async def script(body: SuspensionRequest) -> dict[str, str]:
    """Execute the suspension on the MikroTik device."""
    try:
        uc = get_suspension_use_cases()
        await uc.execute(
            spreadsheet_name=body.SPREADSHEET_NAME,
            mikrotik_ip=body.IP_MIKROTIK,
            date=body.DATE,
        )
        return {"message": "done"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Options endpoints ─────────────────────────────────────────

DEFAULT_OPTIONS: list[str] = [
    "192.168.2.238",
    "64.76.121.146",
    "64.76.121.147",
    "64.76.121.143",
    "64.76.121.243",
    "168.194.32.50",
    "168.194.32.71",
    "168.194.32.21",
    "168.194.32.14",
    "168.194.34.196",
    "168.194.34.197",
]


@router.post("/addOptions")
async def add_options() -> dict[str, str]:
    """Insert the hardcoded default IP options into MongoDB."""
    try:
        uc = get_options_use_cases()
        await uc.add_defaults(DEFAULT_OPTIONS)
        return {"message": "Datos agregados correctamente"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/readOptions")
async def read_options() -> dict[str, list[str]]:
    """Return all stored option IPs."""
    try:
        uc = get_options_use_cases()
        data = await uc.list_options()
        return {"data": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/addDoc")
async def add_doc(body: AddOptionRequest) -> dict[str, str]:
    """Add a single option IP."""
    try:
        uc = get_options_use_cases()
        await uc.add_option(body.option)
        return {"message": "Documento agregado correctamente"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
