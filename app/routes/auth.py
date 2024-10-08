from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import database, schemas, models, utils, oauth2
router = APIRouter(tags=["Authentication"])
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/login',response_model=schemas.Token) # stores in a field called username not email
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db: Session = Depends(get_db)):
    #return username = 
    #password=
    user = db.query(models.User).filter(models.User.email ==  user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentials")
    #crete a token and retun it
    access_token = oauth2.create_access_token(data={"user_id":user.id})
    return {"access_token" : access_token,"token_type":"bearer"}
    