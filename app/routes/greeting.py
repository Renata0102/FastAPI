from fastapi import APIRouter


router = APIRouter()


@router.get('/', summary='The view for opening the root')
def hello_func():
    '''The output of the inscription 'Hello!' when opening the root'''
    return('Hello!')
