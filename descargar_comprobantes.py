import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Preguntar al usuario por el año, mes y día que necesita
anio_input = input("Introduce el año que deseas (por ejemplo, 2023): ")
mes_input = input("Introduce el mes que deseas descargar (1 para enero, 2 para febrero, etc.): ")
dia_input = input("Introduce el día que deseas (1 para el primer día del mes, o escribe 'todos' para ver todo el mes): ")

# Diccionario para convertir los números de mes a nombres
meses = {
    "1": "ENERO", "2": "FEBRERO", "3": "MARZO", "4": "ABRIL", "5": "MAYO",
    "6": "JUNIO", "7": "JULIO", "8": "AGOSTO", "9": "SEPTIEMBRE", "10": "OCTUBRE",
    "11": "NOVIEMBRE", "12": "DICIEMBRE"
}

# Validar el mes ingresado
try:
    anio = int(anio_input)
    mes = int(mes_input)
    if mes < 1 or mes > 12:
        raise ValueError("El mes debe estar entre 1 y 12.")
    
    mes_nombre = meses[str(mes)]  # Obtener el nombre del mes según el número

    # Si el usuario escribe "todos", lo manejaremos como tal
    if dia_input.lower() == "todos":
        dia = "todos"
    else:
        dia = int(dia_input)
        if dia < 1 or dia > 31:
            raise ValueError("El día debe estar entre 1 y 31.")
except ValueError as e:
    print(f"Error: {e}")
    exit()

# Crear la carpeta de descarga si no existe
directorio_descarga = os.path.join(os.getcwd(), mes_nombre)  # Carpeta con el nombre del mes
if not os.path.exists(directorio_descarga):
    os.makedirs(directorio_descarga)
    print(f"Directorio creado: {directorio_descarga}")

# Configurar Chrome para que descargue los archivos en el directorio especificado
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()

# Configuraciones para la descarga automática
prefs = {
    "download.default_directory": directorio_descarga,  # Carpeta de descarga
    "download.prompt_for_download": False,  # No preguntar dónde descargar
    "profile.default_content_settings.popups": 0,  # Deshabilitar popups
    "safebrowsing.enabled": "false"  # Evitar la advertencia de archivos dañinos
}
options.add_experimental_option("prefs", prefs)

# Hacer que el navegador se abra en pantalla completa
options.add_argument("--start-maximized")

# Inicializar el navegador Chrome con las opciones
driver = webdriver.Chrome(service=service, options=options)

# URL de inicio de sesión directo del SRI proporcionado
driver.get("https://srienlinea.sri.gob.ec/auth/realms/Internet/protocol/openid-connect/auth?client_id=app-sri-claves-angular&redirect_uri=https%3A%2F%2Fsri.gob.ec")

# Esperar unos segundos para que cargue la página de inicio de sesión
time.sleep(5)

# Buscar el campo de usuario (RUC) e ingresar los datos
wait = WebDriverWait(driver, 30)
usuario = wait.until(EC.presence_of_element_located((By.ID, "usuario")))  # Ajusta el ID si es necesario
usuario.send_keys("0992798238001")  # Introduce el RUC

# Buscar el campo de contraseña
clave = wait.until(EC.presence_of_element_located((By.ID, "password")))  # Cambiado el ID a "password"
clave.send_keys("LAYH8001")  # Introduce la clave

# Enviar el formulario (iniciar sesión)
clave.send_keys(Keys.RETURN)

# Esperar unos segundos para que se procese el inicio de sesión
time.sleep(10)

# Ir a la sección de "Comprobantes Electrónicos Recibidos"
facturacion_menu = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ui-panelmenu-header.ui-state-default")))
driver.execute_script("arguments[0].click();", facturacion_menu)
menu_contenido = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ui-panelmenu-content-wrapper")))
driver.execute_script("arguments[0].style.height = 'auto';", menu_contenido)
time.sleep(2)

comprobantes_recibidos_menu = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Comprobantes electrónicos recibidos']")))
driver.execute_script("arguments[0].click();", comprobantes_recibidos_menu)

# Esperar a que cargue la página de búsqueda de comprobantes
time.sleep(5)

# Seleccionar el año, mes y día como lo hicimos antes
anio_dropdown = wait.until(EC.presence_of_element_located((By.ID, "frmPrincipal:ano")))
select_anio = Select(anio_dropdown)
select_anio.select_by_value(str(anio))

mes_dropdown = wait.until(EC.presence_of_element_located((By.ID, "frmPrincipal:mes")))
select_mes = Select(mes_dropdown)
select_mes.select_by_value(str(mes))

dia_dropdown = wait.until(EC.presence_of_element_located((By.ID, "frmPrincipal:dia")))
select_dia = Select(dia_dropdown)
if dia == "todos":
    select_dia.select_by_visible_text("Todos")
else:
    select_dia.select_by_value(str(dia))

# Hacer clic en el botón de "Consultar" para buscar los comprobantes
consultar_button = wait.until(EC.presence_of_element_located((By.ID, "btnRecaptcha")))
driver.execute_script("arguments[0].click();", consultar_button)
print("Hicimos clic en el botón de Consultar.")

# Esperar a que los comprobantes aparezcan después de la consulta
time.sleep(10)

# Función para descargar comprobantes en la página actual
def descargar_comprobantes():
    comprobantes = driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkXml')]")
    print(f"Encontrados {len(comprobantes)} comprobantes para descargar en esta página.")
    
    for i, comprobante in enumerate(comprobantes):
        try:
            driver.execute_script("arguments[0].click();", comprobante)
            print(f"Descargando comprobante {i+1} en esta página...")
            time.sleep(5)  # Esperar un poco entre descargas
        except Exception as e:
            print(f"Error al descargar el comprobante {i+1}: {e}")

# Descargar comprobantes de la primera página
descargar_comprobantes()

# Navegar por las páginas y descargar comprobantes
while True:
    try:
        # Verificar si hay un botón de siguiente página habilitado
        boton_siguiente = driver.find_element(By.CSS_SELECTOR, "span.ui-paginator-next.ui-state-default.ui-corner-all")
        
        if "ui-state-disabled" not in boton_siguiente.get_attribute("class"):
            print("Cambiando a la siguiente página...")
            driver.execute_script("arguments[0].click();", boton_siguiente)
            time.sleep(5)  # Esperar a que cargue la siguiente página
            descargar_comprobantes()  # Descargar los comprobantes de la nueva página
        else:
            print("No hay más páginas.")
            break
    except Exception as e:
        print(f"No se encontró el botón de siguiente página o hubo un error: {e}")
        break

# Esperar un poco para asegurarse de que las descargas se completen
time.sleep(20)

# Mantener el navegador abierto para verificar (quitar el comentario si quieres cerrar el navegador al final)
# driver.quit()
