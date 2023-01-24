from flask import Flask , request,render_template
import requests
import json
import psycopg2
import random
app = Flask(__name__)
app.config['ERROR_MESSAGE']=""


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/validate',methods=['POST'])    
def validate():
        iterations = int(request.form['iterations'])
        for i in range(iterations):
            id = generate_random_id()
            is_valid, message = validate_ecuador_id(id)
            if is_valid:
                info = get_person_info(id)
                if info:
                    save_to_db(info)
                    print(f'Guardado en la base de datos: {id}')
            else:
                print(f'No se pudo obtener información para: {id}')
        else:
            print(f'Cédula inválida: {id}')
        return 'Proceso finalizado'
def generate_random_id():
    region = random.randint(1,24)
    if region < 10:
        region = f'0{region}'
    else:
        region = str(region)
    id = region
    for i in range(8):
        id += str(random.randint(0,9))
        print(id)     
    return id
        

def validate_ecuador_id(id):
    if len(id) != 10:
        print(id)
        return True, '''<h1>La cédula es válida</h1> '''
                    
    region = int(id[:2])
    if region < 1 or region > 24:
        return False, '''<h1>Esta cédula no pertenece a ningun establecamiento</h1>'''
    last_digit = int(id[9])
    par = int(id[1]) + int(id[3]) + int(id[5]) + int(id[7])
    num1 = int(id[0])*2
    if num1 > 9:
        num1 -= 9
    num3 = int(id[2])*2
    if num3 > 9:
        num3 -= 9
    num5 = int(id[4])*2
    if num5 > 9:
        num5 -= 9
    num7 = int(id[6])*2
    if num7 > 9:
        num7 -= 9
    num9 = int(id[8])*2
    if num9 > 9:
        num9 -= 9
    imp = num1 + num3 + num5 + num7 + num9
    all_sum = par + imp
    first_digit_sum = str(all_sum)[0]
    docena = (int(first_digit_sum) + 1)*10
    validator_digit = docena - all_sum
    if validator_digit == 10:
        validator_digit = 0
    if validator_digit == last_digit:
        return True,'''<h1>La cédula es válida</h1>'''
    else:
        return False, '''<h1>La cédula no es válida</h1>
    <form method="POST">
                <input type="submit" value="Submit"><br>
                     
               </form>
    '''

def get_person_info(id):
     url = f'https://msbp.trabajo.gob.ec/mdt-services/dinardap/registro-civil-identificacion/{id}/false'
     response= requests.get(url)
     if(response.status_code == 200):
         return json.loads(response.text)
     return None
 
def save_to_db(info):
    connection= psycopg2.connect(user="postgres",
                                 password="123456",
                                 host="localhost",
                                 port="5432",
                                 database="identityEcuador")
    cursor= connection.cursor()
    if    "segundoNombre" in info:
            segundoNombre = info["segundoNombre"]
    else:
        segundoNombre = None
    
    if "apellidoMaterno" in info:
        apellidoMaterno = info["apellidoMaterno"]
    else:
        apellidoMaterno = None
    
    if "apellidoPaterno" in info:
        apellidoPaterno = info["apellidoPaterno"]
    else:
        apellidoPaterno= None
        
    query = """INSERT INTO person_info (cedula, nombre_completo,apellido_paterno,apellido_materno, primer_nombre,
            segundo_nombre, genero, condicion_ciudadano,fecha_nacimiento, lugar_nacimiento, nacionalidad, estado_civil, conyuge, domicilio, calles_domicilio, numero_casa, fecha_matrimonio, lugar_matrimonio, fecha_nacimiento_date, apellidos, nombres, provincia_domicilio, ciudad_domicilio, parroquia_domicilio, provincia_lugar_nacimiento, ciudad_lugar_nacimiento, parroquia_lugar_nacimiento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (
                info["cedula"], info["nombreCompleto"], apellidoPaterno,apellidoMaterno,
              info["primerNombre"], segundoNombre, info["genero"], info["condicionCiudadano"], 
              info["fechaNacimiento"], info["lugarNacimiento"], info["nacionalidad"], info["estadoCivil"],
              info["conyuge"], info["domicilio"], info["callesDomicilio"], info["numeroCasa"],
              info["fechaMatrimonio"], info["lugarMatrimonio"], info["fechaNacimientoDate"], 
              info["apellidos"], 
              info["nombres"],
              info["provinciaDomicilio"], info["ciudadDomicilio"], info["parroquiaDomicilio"], 
              info["provinciaLugarNacimiento"], info["ciudadLugarNacimiento"], info["parroquiaLugarNacimiento"])
    
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
if __name__ == '__main__':
    app.run(debug=True)