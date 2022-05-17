from fastapi import FastAPI, Depends, Query, Path
from uvicorn import run as run_uvicorn
import sys, db


app = FastAPI()



if __name__ == '__main__':
    if sys.argv.__len__() > 1:
        args = sys.argv
        if args[1] == 'create':
            # create database
            db.create()
        elif args[1] == 'drop':
            db.drop()
    run_uvicorn('main:app', reload=True)