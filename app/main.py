from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas
from . import db_models as models
from .database import engine, get_db
from typing import List
from .schemas import UserLogin



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/users/", response_model=schemas.UserIDResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, user=user)
    return {"id": db_user.id}


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.model_dump().items():  # Cambiado dict() a model_dump()
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}


@app.post("/users/{user_id}/subscriptions/", response_model=schemas.Subscription)
def create_subscription_for_user(
    user_id: int, subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)
):
    return crud.create_subscription(db=db, subscription=subscription, user_id=user_id)


@app.get("/users/{user_id}/subscription", response_model=schemas.Subscription)
def read_subscription_for_user(user_id: int, db: Session = Depends(get_db)):
    db_subscription = crud.get_user_subscription(db, user_id=user_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="No active subscription")
    return db_subscription


@app.post("/users/{user_id}/reviews/", response_model=schemas.Review)
def create_review_for_user(user_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_review(db=db, review=review, user_id=user_id)

@app.get("/reviews/{review_id}", response_model=schemas.Review)
def read_review(review_id: int, db: Session = Depends(get_db)):
    db_review = crud.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review


@app.put("/reviews/{review_id}", response_model=schemas.Review)
def update_review(review_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    db_review = crud.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    for key, value in review.model_dump().items():  # Cambiado dict() a model_dump()
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review


@app.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = crud.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(db_review)
    db.commit()
    return {"detail": "Review deleted"}



@app.post("/login/", response_model=schemas.UserIDResponse)
def register_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user = crud.get_user_by_email_and_password(db, email=user.email, password=user.password)

    if db_user:
        return {"id": db_user.id}  # Si el usuario ya existe, devolver solo el id

    # Si no existe, devolvemos un error
    raise HTTPException(status_code=404, detail="User not found")
