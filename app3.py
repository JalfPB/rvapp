import sys
from pymongo import MongoClient
from geopy import distance
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit
import webbrowser
import folium
from PyQt5.QtGui import QFont


class VentanaBusqueda(QWidget):
    def __init__(self):
        super().__init__()

        # Define the font for the texts
        font = QFont()
        font.setPointSize(12)

        # Define the widgets of the interface
        self.setWindowTitle("Búsqueda de puntos de interés")
        self.setGeometry(100, 100, 400, 200)

        self.label_direccion = QLabel("Dirección:")
        self.label_direccion.setFont(font)
        self.input_direccion = QLineEdit()

        self.button_buscar_monumentos = QPushButton("Buscar Monumentos")
        self.button_buscar_monumentos.setFont(font)
        self.button_buscar_monumentos.setStyleSheet("background-color: #4CAF50; color: white;")

        self.button_buscar_farmacias = QPushButton("Buscar Farmacias")
        self.button_buscar_farmacias.setFont(font)
        self.button_buscar_farmacias.setStyleSheet("background-color: #4CAF50; color: white;")

        self.button_buscar_restaurantes = QPushButton("Buscar Restaurantes")
        self.button_buscar_restaurantes.setFont(font)
        self.button_buscar_restaurantes.setStyleSheet("background-color: #4CAF50; color: white;")

        self.button_buscar_todos = QPushButton("Buscar Todos")
        self.button_buscar_todos.setFont(font)
        self.button_buscar_todos.setStyleSheet("background-color: #4CAF50; color: white;")

        self.label_latitud = QLabel("Latitud:")
        self.label_latitud.setFont(font)
        self.input_latitud = QLineEdit()

        self.label_longitud = QLabel("Longitud:")
        self.label_longitud.setFont(font)
        self.input_longitud = QLineEdit()

        self.label_distancia_minima = QLabel("Distancia mínima (en metros):")
        self.label_distancia_minima.setFont(font)
        self.input_distancia_minima = QLineEdit()

        self.label_distancia_maxima = QLabel("Distancia máxima (en metros):")
        self.label_distancia_maxima.setFont(font)
        self.input_distancia_maxima = QLineEdit()

        # Define the layouts
        hbox_direccion = QHBoxLayout()
        hbox_direccion.addWidget(self.label_direccion)
        hbox_direccion.addWidget(self.input_direccion)

        hbox_latitud = QHBoxLayout()
        hbox_latitud.addWidget(self.label_latitud)
        hbox_latitud.addWidget(self.input_latitud)

        hbox_longitud = QHBoxLayout()
        hbox_longitud.addWidget(self.label_longitud)
        hbox_longitud.addWidget(self.input_longitud)

        hbox_distancia_minima = QHBoxLayout()
        hbox_distancia_minima.addWidget(self.label_distancia_minima)
        hbox_distancia_minima.addWidget(self.input_distancia_minima)

        hbox_distancia_maxima = QHBoxLayout()
        hbox_distancia_maxima.addWidget(self.label_distancia_maxima)
        hbox_distancia_maxima.addWidget(self.input_distancia_maxima)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_direccion)
        vbox.addWidget(self.button_buscar_monumentos)
        vbox.addWidget(self.button_buscar_farmacias)
        vbox.addWidget(self.button_buscar_restaurantes)
        vbox.addWidget(self.button_buscar_todos)
        vbox.addLayout(hbox_latitud)
        vbox.addLayout(hbox_longitud)
        vbox.addLayout(hbox_distancia_minima)
        vbox.addLayout(hbox_distancia_maxima)

        self.setLayout(vbox)


class VentanaResultados(QWidget):
    def __init__(self):
        super().__init__()
        self.coordenadas = []  # Initialize the coordinates list

        self.setWindowTitle("Resultados de la búsqueda")
        self.setGeometry(500, 100, 600, 400)

        self.text_area = QTextEdit()
        vbox = QVBoxLayout()
        vbox.addWidget(self.text_area)

        # Add a QLabel to the vertical layout
        self.image_label = QLabel()
        vbox.addWidget(self.image_label)

        self.setLayout(vbox)

    def agregar_resultado(self, titulo, resultado, long, lat, category=None, opening_hours=None, uri=None):
        print(f"Adding result: {titulo}, {resultado}, {long}, {lat}, {category}, {opening_hours}, {uri}")
        self.text_area.append(f"<b>{titulo}</b>")
        self.text_area.append(f"<p>{str(resultado)}</p>")
        if category:
            self.text_area.append(f"<p>Categoría: {category}</p>")
        if opening_hours:
            self.text_area.append(f"<p>Horario de apertura: {opening_hours}</p>")
        if uri:
            self.text_area.append(f"<p>URI: {uri}</p>")
        self.text_area.append(f"<p>Longitud: {long}</p>")
        self.text_area.append(f"<p>Latitud: {lat}</p>")
        self.text_area.append("<br>")
        # Append coordinates to the list
        self.coordenadas.append((lat, long))

    def limpiar_resultados(self):
        self.text_area.clear()
        self.coordenadas.clear()  # Clear the coordinates list


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Puntos de interés")
        self.setGeometry(200, 200, 800, 600)

        self.ventana_busqueda = VentanaBusqueda()
        self.ventana_resultados = VentanaResultados()

        self.ventana_busqueda.button_buscar_monumentos.clicked.connect(
            lambda: self.buscar_puntos_de_interes(tipo="monumentos")
        )
        self.ventana_busqueda.button_buscar_farmacias.clicked.connect(
            lambda: self.buscar_puntos_de_interes(tipo="farmacias")
        )
        self.ventana_busqueda.button_buscar_restaurantes.clicked.connect(
            lambda: self.buscar_puntos_de_interes(tipo="restaurantes")
        )
        self.ventana_busqueda.button_buscar_todos.clicked.connect(
            lambda: self.buscar_puntos_de_interes(tipo="todos")
        )

        hbox = QHBoxLayout()
        hbox.addWidget(self.ventana_busqueda)
        hbox.addWidget(self.ventana_resultados)

        self.setLayout(hbox)
        self.show()

    def buscar_puntos_de_interes(self, tipo="todos"):
        # Connection to the database
        uri = "mongodb://localhost:27017/rvapp"
        client = MongoClient(uri)
        db = client.rvapp

        # Get the collections
        collection_r = db.restaurantes
        collection_m = db.monumentos
        collection_f = db.farmacias

        # Ask for the user's location
        latitud = float(self.ventana_busqueda.input_latitud.text())
        longitud = float(self.ventana_busqueda.input_longitud.text())

        # Ask for the minimum and maximum distance in meters
        min_distancia = float(self.ventana_busqueda.input_distancia_minima.text())
        max_distancia = float(self.ventana_busqueda.input_distancia_maxima.text())

        # Create a point with the user's location
        user_location = (latitud, longitud)
        # Create a map centered on the user's coordinates
        mapa = folium.Map(location=[latitud, longitud], zoom_start=15)

        # Add a marker for the user's location
        folium.Marker(location=[latitud, longitud], icon=folium.Icon(color='red')).add_to(mapa)

        # Clear existing results and add markers to the map
        self.ventana_resultados.limpiar_resultados()

        # Define colors for each point type
        point_colors = {
            "restaurantes": "green",
            "monumentos": "blue",
            "farmacias": "orange",
        }

        if tipo == "todos" or tipo == "restaurantes":
            result_r = collection_r.find({})
            for r in result_r:
                # Get the restaurant's location
                lat_rest = float(r['geo_lat'])
                lon_rest = float(r['geo_long'])
                rest_location = (lat_rest, lon_rest)

                # Calculate the distance from the user to the restaurant
                dist_rest = distance.distance(user_location, rest_location).meters

                # If the distance is within the range, add the restaurant to the results list
                if min_distancia <= dist_rest <= max_distancia:
                    categoria = None
                    if 'om_categoriaRestaurante' in r:
                        categoria = r['om_categoriaRestaurante']
                    self.ventana_resultados.agregar_resultado(
                        "*** Restaurante encontrado a una distancia de {} metros:".format(dist_rest),
                        r['rdfs_label'], r['geo_long'], r['geo_lat'], category=categoria
                    )

                    # Add marker to the map with color
                    folium.Marker(
                        location=[r['geo_lat'], r['geo_long']],
                        popup=f"<b>{r['rdfs_label']}</b><br>Categoría: {categoria}<br>Longitud: {r['geo_long']}<br>Latitud: {r['geo_lat']}",
                        icon=folium.Icon(color=point_colors["restaurantes"])
                    ).add_to(mapa)

        if tipo == "todos" or tipo == "monumentos":
            result_m = collection_m.find({})
            for m in result_m:
                # Get the monument's location
                lat_mon = float(m['geo_lat'])
                lon_mon = float(m['geo_long'])
                mon_location = (lat_mon, lon_mon)

                # Calculate the distance from the user to the monument
                dist_mon = distance.distance(user_location, mon_location).meters

                # If the distance is within the range, add the monument to the results list
                if min_distancia <= dist_mon <= max_distancia:
                    self.ventana_resultados.agregar_resultado(
                        "*** Monumento encontrado a una distancia de {} metros:".format(dist_mon),
                        m['rdfs_label'], m['geo_long'], m['geo_lat'], uri=m['uri']
                    )

                    # Add marker to the map with color
                    folium.Marker(
                        location=[m['geo_lat'], m['geo_long']],
                        popup=f"<b>{m['rdfs_label']}</b><br>URI: {m['uri']}<br>Longitud: {m['geo_long']}<br>Latitud: {m['geo_lat']}",
                        icon=folium.Icon(color=point_colors["monumentos"])
                    ).add_to(mapa)

        if tipo == "todos" or tipo == "farmacias":
            result_f = collection_f.find({})
            for f in result_f:
                # Get the pharmacy's location
                lat_farm = float(f['geo_lat'])
                lon_farm = float(f['geo_long'])
                farm_location = (lat_farm, lon_farm)

                # Calculate the distance from the user to the pharmacy
                dist_farm = distance.distance(user_location, farm_location).meters

                # If the distance is within the range, add the pharmacy to the results list
                if min_distancia <= dist_farm <= max_distancia:
                    opening_hours = f['schema_openingHours'] if 'schema_openingHours' in f else None
                    self.ventana_resultados.agregar_resultado(
                        "*** Farmacia encontrada a una distancia de {} metros:".format(dist_farm),
                        f['schema_name'], f['geo_long'], f['geo_lat'], opening_hours=opening_hours
                    )

                    # Add marker to the map with color
                    folium.Marker(
                        location=[f['geo_lat'], f['geo_long']],
                        popup=f"<b>{f['schema_name']}</b><br>Horario de apertura: {opening_hours}<br>Longitud: {f['geo_long']}<br>Latitud: {f['geo_lat']}",
                        icon=folium.Icon(color=point_colors["farmacias"])
                    ).add_to(mapa)

        # Save the map
        mapa.save("mapa.html")

        # Open the HTML file in a new browser window
        webbrowser.open("mapa.html", new=2)


if __name__ == "__main__":
    app = QApplication([])

    # Connection to the database
    uri = "mongodb://localhost:27017/rvapp"
    client = MongoClient(uri)
    db = client.rvapp

    # Get the collections
    collection_r = db.restaurantes
    collection_m = db.monumentos
    collection_f = db.farmacias

    ventana = App()
    sys.exit(app.exec_())

       
