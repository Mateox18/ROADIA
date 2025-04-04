#include <iostream>
//Libreria basica
#include <vector>
//Para usar listas
#include <queue>
//Cola de prioridad
#include <unordered_map> 
//Para usar diccionarios como en python
#include <limits>
//Operaciones matematicas complejas
#include <string>
#include <utility>
//Uso de strings
#include <nlohmann/json.hpp>
//Trabajar con json
using namespace std;

//Cada nodo va a almacenar la informacion de las conexiones
struct Nodo {
    //Guarda el nombre del nodo
    string nombre;
    //
    unordered_map<string, pair<int, bool>> conexiones; // {destino, (costo, accesible)}
};
