from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .deps import get_current_user
from .console_runner import run_console_task
router = APIRouter(prefix='/api/console', tags=['console'])
class ConsoleReq(BaseModel): module: Optional[str]=None; function: Optional[str]=None; params: Optional[Dict[str, Any]]=None; script: Optional[str]=None; args: Optional[List[Any]]=None
@router.post('/run')
def run(req: ConsoleReq, user=Depends(get_current_user)):
    return {'ok': True, 'result': run_console_task(req)}
