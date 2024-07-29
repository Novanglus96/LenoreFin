from ninja import Schema
from datetime import date, timedelta, datetime


# The class NoteIn is a schema for validating a Note.
class NoteIn(Schema):
    note_text: str
    note_date: date


# The class NoteOut is a schema for representing a Note.
class NoteOut(Schema):
    id: int
    note_text: str
    note_date: date
