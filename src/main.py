import jwt
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Security, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator, Any
from httpx import AsyncClient

from src.app.routers.task_router import router as task_router
from src.app.routers.auth_router import router as auth_router
from src.app.routers.event_router import router as event_router
from src.app.routers.calendar_router import router as calendar_router
from src.configs.database import engine, Base
from src.configs.logger import log
from src.configs.settings import settings
from src.configs.auth import azure_scheme

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    log.info(f"Starting up {settings.APP_NAME}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables created")

    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()
    
    yield  # This is where the FastAPI app runs
    
    # Shutdown
    log.info(f"Shutting down {settings.APP_NAME}")
    await engine.dispose()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan, swagger_ui_init_oauth={
    'usePkceWithAuthorizationCodeGrant': True,
    'clientId': settings.OPENAPI_CLIENT_ID,
    'appName': settings.APP_NAME,
    # 'scopes': ['openid', 'profile', 'email', 'offline_access', 'User.Read', 'Calendars.Read', 'Calendars.ReadWrite'],
    # 'scopes': ['openid', 'profile', 'email', 'offline_access', 'User.Read'],
    # 'scopes': 'openid profile email offline_access User.Read',
    # 'scopeSeparator': ' ',
})

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

# @app.get("/")
@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    return {"message": "Hello World"}

@app.get(
    '/hello-graph',
    summary='Fetch graph API using OBO',
    name='graph',
    operation_id='helloGraph',
    dependencies=[Depends(azure_scheme)],
)
async def graph_world(request: Request) -> Any:  # noqa: ANN401
    """
    An example on how to use "on behalf of"-flow to fetch a graph token and then fetch data from graph.
    """
    async with AsyncClient() as client:
        # Use the users access token and fetch a new access token for the Graph API
        common_tenant = 'common'

        obo_response: httpx.Response = await client.post(
            # f'https://login.microsoftonline.com/{settings.AZURE_AD_TENANT_ID}/oauth2/v2.0/token',
            f'https://login.microsoftonline.com/{common_tenant}/oauth2/v2.0/token',
            data={
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'client_id': settings.APP_CLIENT_ID,
                'client_secret': settings.AZURE_AD_CLIENT_SECRET,
                'assertion': request.state.user.access_token,
                'scope': 'https://graph.microsoft.com/user.read',
                'requested_token_use': 'on_behalf_of',
            },
        )

        if obo_response.is_success:
            # Call the graph `/me` endpoint to fetch more information about the current user, using the new token
            graph_response: httpx.Response = await client.get(
                'https://graph.microsoft.com/v1.0/me',
                headers={'Authorization': f'Bearer {obo_response.json()["access_token"]}'},
            )
            graph = graph_response.json()
        else:
            graph = 'skipped'

        # Return all the information to the end user
        return (
            {'claims': jwt.decode(request.state.user.access_token, options={'verify_signature': False})}
            | {'obo_response': obo_response.json()}
            | {'graph_response': graph}
        )


app.include_router(task_router, prefix=settings.API_V1_STR + "/tasks", tags=["tasks"])
app.include_router(auth_router, prefix=settings.API_V1_STR  + "/auth", tags=["authentication"])
app.include_router(event_router, prefix=settings.API_V1_STR + "/events", tags=['events'])
app.include_router(calendar_router, prefix=settings.API_V1_STR + "/calendars", tags=['calendars'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
