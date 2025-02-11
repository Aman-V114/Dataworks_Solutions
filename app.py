from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import functions


app = FastAPI()

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description")):
    if not task:
        raise HTTPException(status_code=400, detail="Task description is required")
    
    try:
        response = await functions.chat_with_aiproxy(task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in task: {str(e)}")
    
    return JSONResponse(content={"message": response}, status_code=200)


@app.get("/read")
async def read_file(request: Request):
    file_path = request.query_params.get('path')
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return JSONResponse(content={"content": content}, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)