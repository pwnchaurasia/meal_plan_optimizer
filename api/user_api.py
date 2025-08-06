from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter(prefix="/auth", tags=["auth"])

