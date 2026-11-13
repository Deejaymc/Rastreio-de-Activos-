import os
import sys

# Se alguém executar python app.py, delegamos para uvicorn rodando app.main:app
if __name__ == "__main__":
    import uvicorn
    # Remove o próprio script do caminho de módulo para permitir importar o pacote 'app'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if sys.path and sys.path[0] == current_dir:
        sys.path.pop(0)
    sys.path.insert(0, current_dir)
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

