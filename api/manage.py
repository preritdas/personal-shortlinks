"""CRUD operations for the links."""
from fastapi import APIRouter
from pydantic import field_validator, BaseModel, Field

from datetime import datetime

from shortlinks import create_shortlink, delete_shortlink, change_expiration
from shortlinks.database import SHORTLINKS
from keys import KEYS


router = APIRouter()


class LinkJob(BaseModel):
    """Link model."""
    code: str
    url: str
    expiration: str = Field("3000-01-01", description="Expiration date and time in YYYY-MM-DD format.")
    password: str = Field("", description="Password for management.")

    @field_validator("expiration")
    def expiration_datetime(cls, v):
        """Validate expiration."""
        if v:
            return datetime.strptime(v, "%Y-%m-%d")

        return v


class CodeJob(BaseModel):
    """Code model."""
    code: str
    password: str = Field("", description="Password for management.")


@router.post("/create")
async def create(shortlink: LinkJob) -> str:
    """Create a shortlink."""
    # Validate the password
    if shortlink.password != KEYS.General.manage_pwd:
        return "Incorrect password."

    res = create_shortlink(shortlink.url, shortlink.code, shortlink.expiration)

    if res:
        return "Shortlink created successfully."

    return "Shortlink already exists."


@router.post("/delete")
async def delete(code: CodeJob) -> str:
    """Delete a shortlink."""
    # Validate the password
    if code.password != KEYS.General.manage_pwd:
        return "Incorrect password."

    res = delete_shortlink(code.code)

    if res:
        return "Shortlink deleted successfully."

    return "Shortlink doesn't exist."


class ExpirationChangeJob(BaseModel):
    """Expiration change model."""
    code: str
    new_expiration: str = Field("3000-01-01", description="Expiration date and time in YYYY-MM-DD format.")
    password: str = Field("", description="Password for management.")

    @field_validator("new_expiration")
    def expiration_datetime(cls, v):
        """Validate expiration."""
        if v:
            return datetime.strptime(v, "%Y-%m-%d")

        return v


@router.post("/change-expiration")
async def change_expire(expiration_change: ExpirationChangeJob) -> str:
    """Change the expiration of all shortlinks matching the code."""
    # Validate the password
    if expiration_change.password != KEYS.General.manage_pwd:
        return "Incorrect password."

    res = change_expiration(expiration_change.code, expiration_change.new_expiration)

    if res:
        return "Shortlink expiration changed successfully."

    return "Shortlink doesn't exist."


@router.get("/clicks/{code}")
async def get_clicks(code: str, password: str) -> dict:
    """See the clicks for a shortlink."""
    # Validate the password
    if password != KEYS.General.manage_pwd:
        return "Incorrect password."

    if not (shortlink := SHORTLINKS.find_one({"code": code})):
        return "Shortlink not found."

    if not "clicks" in shortlink:
        return {"clicks": []}

    return {"clicks": shortlink["clicks"]}
