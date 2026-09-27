
from fastapi import FastAPI, HTTPException
from database import Base, engine, SessionLocal
from models import User, Memory, Event
from schemas import UserCreate, MemoryCreate, EventCreate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hindsight Backend API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users")
def create_user(user: UserCreate):
    db = SessionLocal()

    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }


@app.post("/memories")
def create_memory(memory: MemoryCreate):
    db = SessionLocal()

    new_memory = Memory(
        user_id=memory.user_id,
        content=memory.content
    )

    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    db.close()

    return {
        "id": new_memory.id,
        "user_id": new_memory.user_id,
        "content": new_memory.content
    }


@app.get("/memories/{user_id}")
def get_memories(user_id: int):
    db = SessionLocal()

    memories = db.query(Memory).filter(
        Memory.user_id == user_id
    ).all()

    result = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "content": m.content
        }
        for m in memories
    ]

    db.close()

    return result


@app.post("/events")
def create_event(event: EventCreate):
    db = SessionLocal()

    new_event = Event(
        user_id=event.user_id,
        title=event.title,
        description=event.description
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    db.close()

    return {
        "id": new_event.id,
        "user_id": new_event.user_id,
        "title": new_event.title,
        "description": new_event.description
    }


@app.get("/events/{user_id}")
def get_events(user_id: int):
    db = SessionLocal()

    events = db.query(Event).filter(
        Event.user_id == user_id
    ).all()

    result = [
        {
            "id": e.id,
            "user_id": e.user_id,
            "title": e.title,
            "description": e.description
        }
        for e in events
    ]

    db.close()

    return result


print("main.py created successfully!")
