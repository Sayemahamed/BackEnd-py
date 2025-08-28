from API.db import get_async_session
from API.services import MainService
from fastapi import APIRouter, Depends, HTTPException,Request
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import RedirectResponse

main_router = APIRouter()


@main_router.get(
    "/{code}",
    status_code=307,
    response_class=RedirectResponse,
    description="Redirect to original URL",
)
async def redirect(
    code: str,
    request: Request,
    main_service: MainService = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user_data={'ip_address':request.client.host, 'user_agent':request.headers.get('user-agent')}
    url = await main_service.redirect(code, user_data,session)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=url, status_code=307)
