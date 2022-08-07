from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator


from datetime import datetime
from playhouse.db_url import connect

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    FixedCharField,
    IntegerField,
    Model,
    BigIntegerField,
    PrimaryKeyField,
    SQL
)
from playhouse.postgres_ext import ArrayField, JSONField

class MetaRequestModel(Model):
    id = PrimaryKeyField(primary_key=True, unique=True)
    created = DateTimeField(default=datetime.now)
    chain_id = IntegerField()
    owner = FixedCharField(42)
    token = FixedCharField(42)
    recipient = FixedCharField(42)
    recipientAmount = CharField()
    rewardAmount = CharField()
    nonce = CharField()
    deadline = DateTimeField()
    permitSignature = CharField()
    requestSignature = CharField()
    status = BooleanField(default=False)
    
    class Meta:
        table_name = 'meta_requests'

psql_db = connect('postgresext://admin:pjvBbtuepIQCnyxB4TboTp@167.235.227.1:5432/ether', autoconnect=False)
psql_db.bind([MetaRequestModel])

router = APIRouter()

class MetaRequest(BaseModel):
    chain_id: int
    owner: str
    token: str
    recipient: str
    recipientAmount: str
    rewardAmount: str
    nonce: str
    deadline: datetime
    permitSignature: str
    requestSignature: str

    @validator("deadline", pre=True)
    def prepare_deadline(cls, deadline: int):
        return datetime.fromtimestamp(deadline // 1000)

@router.post("/meta_request/add")
def add_request(request: MetaRequest):
    print(MetaRequest)
    with psql_db:
        MetaRequestModel.create(**request.dict())
    return {"message": "ok"}

@router.get("/meta_request/list")
def add_request():
    with psql_db:
        requests = list(MetaRequestModel.select().where(1==1).dicts())
    return {"requests": requests}

@router.get("/meta_request/set_success/{id}")
def update_status(id):
    with psql_db:
        MetaRequestModel.update({MetaRequestModel.status: True}).where(MetaRequestModel.id == id).execute()
    return {"message": "ok"}


def get_app():
    app = FastAPI(title="GINO FastAPI Demo")
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = get_app()