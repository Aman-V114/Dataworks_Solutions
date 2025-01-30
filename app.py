from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/run")
async def run_task(request: Request):
    task_description = request.query_params.get('task')
    
    if not task_description:
        raise HTTPException(status_code=400, detail="Task description is required")
    
    try:
        # Add your task execution logic here
        pass
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in task: {str(e)}")
    
    return JSONResponse(content={"message": f"Task '{task_description}' is running"}, status_code=200)


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
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)