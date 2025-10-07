#Práctica 2: Métodos GET, PUT, POST, DELETE Y PATCH
#Equipo:
#Beltrán Saucedo Axel Alejandro
#Cerón Samperio Lizeth Montserrat
#Higuera Pineda Angel Abraham
#Lorenzo Silva Abad Rey

#Recordar que se debe ejecutar/iniciar el servidor en la terminal
#Con el comando: python -m uvicorn Codigo.Practica2:app --reload
#Al parecer se debe especificar lo de python, ya que puede que no detecte el uvicorn sin el
#Para ver la pagina y realizar operaciones, visitar: http://127.0.0.1:8000/docs

#Importamos los modulos (librerias) necesarias

#FastApi es el modulo principal, HTTPException es un manejador de errores, como el "no encontrado" 
#Status es un modulo de indentificacion de codigos de estado HTTP, como el clasico 404
from fastapi import FastAPI, HTTPException, status
#Pydantic es un modulo para la validacion de datos y la creacion de modelos de datos
from pydantic import BaseModel
#Optional y List son tipos de datos que permiten definir campos opcionales y listas
#Se usan para definir los modelos de datos y las respuestas de la API
from typing import Optional, List

#Creamos la instancia de FastAPI
#Es el corazon de nuestro programa (API)
app = FastAPI(
    #Nombre y descripcion de la API
    title= "Practica 2: Metodos GET, PUT, POST, DELETE Y PATCH",
    description= "API para almacenar, editar, actualizar y borrar la información de los paquetes (items) a ser enviados"
)

#Estructura de los datos con Pydantic

#ItemBase es la estructura base de un item, con los campos ganancia y peso
#Digamos que es lo que tiene cada item
class ItemBase(BaseModel):
    ganancia: float
    peso: float
#Item contiene el indentificador unico (id) y hereda los campos de ItemBase
class Item(ItemBase):
    id: int
#ItemUpdate es una clase especial utilizada para cuando queremos actualizar un item parcialmente
#Los campos son opcionales, ya que podemos querer actualizar solo uno de ellos
#El valor por defecto es None
class ItemUpdate(BaseModel):
    peso: Optional[float] = None
    ganancia: Optional[float] = None

#Variables globales

#Creamos una lista llamada envio para almacenar los items
envio: List[Item] = []
#Variable para tener el control dek ud qye se le asigna a cada item
current_id = 0

#Funciones de la API - Lo importante

#Get: Permite obtener todos los items cuando se accede a la ruta /items/
@app.get("/items/", response_model=list[Item], tags=["Items"])
def get_all_items():
    return envio

#En /items/{item_id} -Se debe especificar el id correcto del objeto

#Get: Permite obtener un item por su id 
@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
def get_item_by_id(item_id: int):
    #Recorremos la lista de items para encontrar el que tiene el id que buscamos
    item = next((item for item in envio if item.id == item_id), None)
    #Si no se encuentra, marcamos un error 404 (no encontrado)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    #Si se encuentra da el item    
    return item

#Post: Permite crear un item nuevo 
#Se devuelve el codigo 201 (creado) si todo sale bien
@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
def create_item(item_data: ItemBase):
    #Accede a la variable global, para poder modificarla e indicar el numero de ids creados
    global current_id
    #Se incrementa el id actual en 1
    current_id += 1
    #Se crea un nuevo item con el id actual y los datos proporcionados
    new_item = Item(id=current_id, **item_data.model_dump())
    #Se agrega el nuevo item a la lista de envio
    envio.append(new_item)
    #Da el nuevo item
    return new_item

#Put: Remplaza un item existente por completo por su id 
@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
def replace_item(item_id: int, item_data: ItemBase):
    #Recorremos la lista de items para encontrar el que tiene el id que buscamos para remplazarlo
    for i, item in enumerate(envio):
        #Si encontramos el id buscado
        if item.id == item_id:
            #Actualiza el item con los nuevos datos
            #Crear un nuevo objeto con el mismo ID y remplaza el antiguo
            updated_item = Item(id=item_id, **item_data.model_dump())
            envio[i] = updated_item
            #Da el item actualizado
            return updated_item
    #Si no se encuentra, marcamos un error 404 (no encontrado)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")

#Patch: Actualiza parcialmente un item por su id 
@app.patch("/items/{item_id}", response_model=Item, tags=["Items"])
def update_item_partially(item_id: int, item_update: ItemUpdate):
    #Busca el item en la lista
    stored_item = next((item for item in envio if item.id == item_id), None)
    #Si no se encuentra, marcamos un error 404 (no encontrado)
    if not stored_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encntrado")
    #Actualiza solo los campos proporcionados en item_update
    update_data = item_update.model_dump(exclude_unset=True)
    #Recoremos los campos a actualizar y los asignamos al item almacenado
    for key, value in update_data.items():
        setattr(stored_item, key, value)
    #Devuelve el item actualizado
    return stored_item

#Delete: Borra un item por su id 
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
def delete_item(item_id: int):
    #Recoore la lista para buscar el item a borrar
    item_to_delete = next((item for item in envio if item.id == item_id), None)
    #Si no se encuentra, marcamos un error 404 (no encontrado)
    if not item_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    #Si se encuentra, lo elimina de la lista
    envio.remove(item_to_delete)
    return
