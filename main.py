# main.py
#TOD EN LA CARPETA DEL PROYECTO  // INSTALACIÓN
#python3 -m venv env
#pip3 install fastapi
#pip3 install "uvicorn[standard]"
#python -m uvicorn main:app --reload

from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import dbLogin
from schema import Token
from login import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_active_user, get_password_hash
from schema import User, UserInDB
app = FastAPI()



@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(dbLogin, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/register")
async def register_user(register_user: UserInDB):
    hashed_password = get_password_hash(register_user.hashed_password)
    user_dict = register_user.dict()
    user_dict.pop("hashed_password")
    user_dict["hashed_password"] = hashed_password
    count = await dbLogin.count_documents({"username": register_user.username})
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso"
        )
    dbLogin.insert_one(user_dict)
