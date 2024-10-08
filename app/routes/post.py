from sqlalchemy import func
from .. import oauth2
from .. import models, schemas
from fastapi import  status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import  List, Optional
from ..database import  SessionLocal

router = APIRouter(prefix="/posts",tags=["Posts"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()







@router.get("/",response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user), 
    limit: int = 10, 
    skip: int = 0, 
    search: Optional[str] = ""
):
    # Query posts with pagination and optional search filter
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # Query for posts with their vote counts
    posts = db.query(
        models.Post, 
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # # Serialize the results into a format that can be returned by FastAPI
    # serialized_results = []
    # for post, vote_count in results:
    #     post_dict = post.__dict__.copy()  # Convert Post object to dictionary
    #     post_dict['votes'] = vote_count   # Add the vote count to the dictionary
    #     serialized_results.append(post_dict)

    return posts

# titlw,str, content str
# bool published post
# create ---->  post status code 201
@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #cursor.execute("""INSERT INTO post (title,content,is_published) VALUES (%s,%s,%s) RETURNING * """,(post.title,post.content,post.is_published))
    #conn.commit()
    #new_post = cursor.fetchone()
    #new_posts = models.Post(title=post.title,content=post.content,is_published=post.is_published)
    print(current_user.email)
    new_posts = models.Post(owner_id=current_user.id,**post.model_dump())
    db.add(new_posts)
    db.commit()
    db.refresh(new_posts)
    return new_posts


# @router.get("/posts/latest")
# def get_latest_post():
#     post = my_posts[len(my_posts)-1]
#     return post


@router.get("/{id}",response_model=schemas.PostOut) # id field represent path parameter
def get_posts(id: int,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #cursor.execute("""SELECT * from post WHERE  eid=%s """,(str(id),))
    #post = cursor.fetchone()
    #print(post)
    post = db.query(
        models.Post, 
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).group_by(models.Post.id).filter(models.Post.id == id).first()
    #print(post)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} was not found")
    
    if post.owner_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform")
    
    return post

# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p['id'] == id:
#             return i
    
        
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #find the index in the array
    #my_post.pop(ind)
   # cursor.execute("""DELETE from post where eid=%s returning *""",(str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if post.owner_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_post(id:int,updated_post: schemas.PostCreate,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #print(post)
    #cursor.execute("""UPDATE post SET title = %s, content=%s, is_published=%s WHERE eid = %s returning *""",(post.title,post.content,post.is_published,str(id)))
    #updated_post = cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if post.owner_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()