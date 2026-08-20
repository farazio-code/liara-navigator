from fastapi import APIRouter, Request, Response, status

from app.api.schemas import CreateSessionResponse, ErrorResponse, SessionSummary


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={429: {"model": ErrorResponse, "description": "Rate limited"}},
)
async def create_anonymous_session(request: Request, response: Response) -> CreateSessionResponse:
    session, csrf_token = request.app.state.session_vault.create_anonymous()
    settings = request.app.state.settings
    response.set_cookie(
        key="ln_session",
        value=str(session.session_id),
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=7200,
        path="/",
    )
    return CreateSessionResponse(
        session=SessionSummary(
            connection_state=session.connection_state,
            idle_expires_at=session.idle_expires_at,
            absolute_expires_at=session.absolute_expires_at,
        ),
        csrf_token=csrf_token,
    )
