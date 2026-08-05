# station-data 


En este proyecto analizo datos de una estación meteorológica de 2000 a 2023 con Pandas y SQL. Los datos son originales y estaban con todo tipo de formatos. Una vez parseados, limpaiados y orenados en una base de datos, los he analizado respondiendo cuestiones relevantes y dibujando gráficas para entenderlos bien. 

La estación meteorológica resgistró en su día en formato antiguo de excel, xls. A medida que pasaron los años, se fueron añadiendo instrumentos nuevos (radiómetro, higrómetro) y cambió la forma de medir junto con los nombres. Poder llegar al final a una base de datos limpia ha sido la parte más difícil. 

Originalmente iba a construir la base de datos incluyendo datos de 1998, 1999 y 2024 pero estos tenían un esquema de datos distinto entonces decidí hacerlo de 2000-2023 analizando 2024 por separado. 
Los datos de la era principal (big era) están en careptas y divididos en excels mensuales.

<p align="center">
  <img src="./images/datafolders.png" alt="Data folders" width="500">
</p>

Se midió (en inglés): `temp`, `humidity`, `vapor_pressure`, `dew_point` y `rain_mm`. Luego se añadió `vapor_deficit`, `radiation` y `radiation_accum`. Las medidas son cada 10 segundos, y cada diez minutos se obtiene una media que va como datapoint al excel mensual. Cada día en el excel tiene obviamente 144 datos climáticos. 

### Parte 1/2: preparar los datos

He tenido que renombrar las columnas corruptas (por ejemplo Mï¿½xima Temperatura). Luego he convertido los tipos de datos y he separado día, hora, minuto para crear más adelante un timestamp y poder hacer operaciones temporales con Pandas. Únicamente he interpolado los datos de septiembre 2024 añadiendo una columna de flag para distinguirlos.

Para detectar valores que no tienen sentido en los datos de 2024 he usado z score que normaliza todo. He mirado todos los datos que estaban a más de 3 desviaciones estándar de la media. Luego me he dado cuenta de que hay magnitudes que no siguen una distribución normal, como `avg_wind_sppeed` que suele tener valores bajos pero ocasionalmente rachas fuertes de viento que hacen una cola larga. 

Para ver las variables de una vistazo he ploteado un gráfico gigante. 

![September 2024 climate distributions](images/september_2024_distributions.png)

Como limpiar 23 años de datos de una sola vez es difícil, primero he ido poco a poco haciendo prototipos de las funciones de python en meses particulares y después generalizándolas. 

Como test he usado el excel `F2001-01.xls`de enero de 2001. En cada excel mensual, después de las medidas diarias venía una columna con un resumen "Total" que he tenido que quitar. Después renombré todo. La columna de hora `H` tenía un formato raro (180 debía ser 18:00) que he parseado con una función. He cambiado la hora de 2400 a 00:00 y he añadido un día a las medidas de medianoche.
He comprobado que no hay huecos temporales en los datos. Par ver que iba bien he ploteado la temperatura de septiembre 2024.

![temperature_example](./images/example_temperature.png)

La parte más intersante ha sido hacer las funciones `load_month_era()` , `load_range()` y verlas funcionar. Para esto he tenido que crear otras funcioens que son específicas para formatos como `load_month_era3()`. 
 
Había datos corruptos en `F2002-01.xls` y `F2006-02.xls`.

Al hacer las gráficas había un salto de *10 en los datos, esto era porque a pesar de mantener la misma etiqueta, las magnitudes de presión pasaron de estar en kPa a hPa sin avisar. Esto he tenido que tenerlo en cuenta en las funciones de carga.

Usar sql para la base de datos ha servido para no tener que ejecutar las funciones de nuevo cada vez que quería usar el dataframe construyéndolo otra vez. (en realidad solo tardaba 23 segundos en cargar, no era demasiado). Antes había creado una función `build.py`que me permite cargar el dataset limpio ejecutando un solo script.

Tener la base en SQL también permite hacer preguntas más interesantes a los datos como: ¿Para cada mes cuál ha sido el salto de temperatura entre el año más caluroso y el más frío para ese mes?, ¿Qué años han tenido una racha de más de 15 días sin llover? o ¿Cuáles han sido las olas de calor definidas como 3 o más días consecutivos en la que la temperatura ha sobrepasado el percentil 95? Todas las 19 queries están en los notebooks. 

### Parte 2/2: analizar los datos

Para el análisis de datos he usado matplotlib y el dataframe de pandas que se cargaba desde un archivo .parquet. Los dibujos:


![anual_temp](./images/anual_temp.png)

(climograma normal)
![climograma](./images/climograma.png)

![missing_values](./images/missing_values.png)

![dew_point](./images/dew_point.png)

![rainfall](./images/rainfall.png)

![temp](./images/temp.png)




## Estructura de archivos 

```data/
  A-1998/ ... A-2024/
  station_data.db
  station_data.parquet

images/
  anual_temp.png
  climograma.png
  datafolders.png
  dew_point.png
  example_temperature.png
  humidity.png
  missing_values.png
  rainfall.png
  september_2024_distributions.png
  temp.png
  vapor_deficit.png
  vapor_pressure.png
  wind_run_histogram.png

notebooks/
  2_era_exploration.ipynb
  3_era_exploration.ipynb
  4_era_exploration.ipynb
  big_era_exploration.ipynb
  data_analysis.ipynb
  database_creation.ipynb
  loader_prototypes.ipynb
  sql_questions.ipynb

src/
  build.py
  loaders.py

LICENSE
README.md
```