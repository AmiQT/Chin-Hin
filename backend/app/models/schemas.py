from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ================================================
# BASE SCHEMAS
# ================================================

class BaseSchema(BaseModel):
    """Base schema with common config."""
    class Config:
        from_attributes = True


# ================================================
# USER SCHEMAS
# ================================================

class UserBase(BaseSchema):
    email: EmailStr
    full_name: str
    department: Optional[str] = None
    role: str = "employee"
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class User(UserBase):
    id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


# ================================================
# LEAVE SCHEMAS
# ================================================

class LeaveTypeBase(BaseSchema):
    name: str
    description: Optional[str] = None
    default_days: int = 0


class LeaveType(LeaveTypeBase):
    id: UUID
    is_active: bool = True
    created_at: datetime


class LeaveBalanceBase(BaseSchema):
    user_id: UUID
    leave_type_id: UUID
    year: int
    total_days: int = 0
    used_days: int = 0
    pending_days: int = 0


class LeaveBalance(LeaveBalanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class LeaveRequestBase(BaseSchema):
    leave_type_id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequest(LeaveRequestBase):
    id: UUID
    user_id: UUID
    total_days: Decimal
    status: str = "pending"
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ================================================
# ROOM BOOKING SCHEMAS
# ================================================

class RoomBase(BaseSchema):
    name: str
    location: Optional[str] = None
    capacity: int = 10
    amenities: Optional[List[str]] = None


class Room(RoomBase):
    id: UUID
    is_active: bool = True
    created_at: datetime


class RoomBookingBase(BaseSchema):
    room_id: UUID
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None


class RoomBookingCreate(RoomBookingBase):
    pass


class RoomBooking(RoomBookingBase):
    id: UUID
    user_id: UUID
    status: str = "confirmed"
    created_at: datetime
    updated_at: datetime


# ================================================
# EXPENSE CLAIM SCHEMAS
# ================================================

class ClaimCategoryBase(BaseSchema):
    name: str
    description: Optional[str] = None
    max_amount: Optional[Decimal] = None


class ClaimCategory(ClaimCategoryBase):
    id: UUID
    is_active: bool = True
    created_at: datetime


class ClaimBase(BaseSchema):
    category_id: UUID
    amount: Decimal
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    claim_date: date = Field(default_factory=date.today)


class ClaimCreate(ClaimBase):
    pass


class Claim(ClaimBase):
    id: UUID
    user_id: UUID
    receipt_data: Optional[dict] = None
    status: str = "pending"
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ================================================
# CONVERSATION SCHEMAS (for AI chat)
# ================================================

class MessageBase(BaseSchema):
    role: str  # user, assistant, system
    content: str
    metadata: Optional[dict] = None


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime


class ConversationBase(BaseSchema):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[Message]] = None


# ================================================
# API RESPONSE SCHEMAS
# ================================================

class APIResponse(BaseSchema):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class PaginatedResponse(BaseSchema):
    success: bool = True
    data: List[dict]
    total: int
    page: int = 1
    per_page: int = 20
