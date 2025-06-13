#!/usr/bin/env python
# coding: utf-8

# ### Importar librerias

# In[1]:


import os
import pandas as pd
import constants_robusto
from constants_robusto import RECURSOS_POR_RUTA
from constants_robusto import COLUMNA_VALOR_PROGRAMA


# In[2]:


pd.set_option('display.float_format', '{:,.2f}'.format)


# ### TO-DOS generales
# 0. Escribir en algún lado del REPO que esta clase corresponde a la primera convocatoria de EFT
# 1. Estandarizar/discernir el nombre la columna ocupación. Existe Ocupación y Ocupacion

# ### Clase general de asignacion

# Objetivo:
# 
# 1 - Implementar una clase general 
# 
# 2 - Implementar las clases de cada ruta heredando las caracteristicas de la clase general
# 

# In[3]:


class AsignacionBase:
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase base para la asignación de recursos a programas educativos.

    Esta clase contiene la interfaz y funcionalidades comunes para todas las rutas de asignación
    (antiguos, viejos, cerrados), tales como validaciones, carga de datos y operaciones genéricas.
    """

    def __init__(self, recursos_disponibles = None):
        """
        Inicializa la asignación con los recursos disponibles específicos para la ruta.

        Parameters:
        - recursos_disponibles (int): Monto total de recursos disponibles para esta ruta.
        """
        self.recursos_disponibles = recursos_disponibles
        self.data = None
        self.__llave_cruce = "CODIGO_PROGRAMA" #llave para cruzar los documentos crudos
        self.ruta_cargar = "Asignacion de cupos/"
        self.ruta_exportar = "Export/"
    
    # TO DO: En el contrato de la función está pendiente especificar las condiciones que se esperan de ruta_archivo_habilitados (archvio que viene de otra area)
    # TO DO: Definir si en esta función van las pruebas de 
    def __cargar_datos_crudos(self, nombre_archivo_habilitados, nombre_archivo_complementario=None):
        """
        Carga y preprocesa los datos de entrada necesarios para la asignación.
    
        Args:
            ruta_archivo_habilitados (str): Ruta a un archivo Excel (.xlsx) que debe contener columnas esperadas 
                según constants_robusto.NOMBRE_COLUMNAS_MAPPING. Debe existir y ser legible por pandas.
                
            ruta_archivo_complementario (str, optional): Ruta a un archivo Pickle (.pkl) que contiene datos adicionales.
                Este archivo debe tener las columnas definidas en constants_robusto.COLUMNAS_PROGRAMAS_EFT_OFERTA.
                Si no se proporciona, se omite la fusión con datos complementarios.
     
        Raises:
            FileNotFoundError: Si alguno de los archivos proporcionados no existe.
        """

        ruta_archivo_habilitados = self.ruta_cargar +  nombre_archivo_habilitados
        ruta_archivo_complementario = self.ruta_cargar + nombre_archivo_complementario
        
        #Validar que existe ruta_archivo_habilitados
        if not os.path.exists(ruta_archivo_habilitados):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo_habilitados}")
            
        # Cargar archivo principal
        Programas_EFT = pd.read_excel(ruta_archivo_habilitados)
        
        # Renombrar algunas columnas
        Programas_EFT = Programas_EFT.rename(columns=constants_robusto.NOMBRE_COLUMNAS_MAPPING)
        
        # Cambiar tipo de los datos
        Programas_EFT = Programas_EFT.astype(constants_robusto.TIPO_COLUMNAS_MAPPING)
    
        # Si hay archivo complementario, cargar y combinar
        if ruta_archivo_complementario is not None:
            
            #Validar que existe el ruta_archivo_complementario
            if not os.path.exists(ruta_archivo_complementario):
                raise FileNotFoundError(f"No se encontró el archivo complementario: {ruta_archivo_complementario}")
                
            Programas_EFT_Oferta = pd.read_pickle(ruta_archivo_complementario)
            Programas_EFT_Oferta = Programas_EFT_Oferta[constants_robusto.COLUMNAS_PROGRAMAS_EFT_OFERTA]
            Programas_EFT_Oferta = Programas_EFT_Oferta.astype(constants_robusto.TIPO_COLUMNAS_MAPPING)
    
            # Unir Programas_EFT y Programas_EFT_Oferta
            Programas_EFT = Programas_EFT.merge(
                Programas_EFT_Oferta,
                how='left',
                on=['CODIGO_PROGRAMA']
            )

            cruzaron = Programas_EFT['cod_CNO'].notna().sum()
            no_cruzaron = Programas_EFT['cod_CNO'].isna().sum()
            print(f"La llave es: {self.__llave_cruce}")
            print(f"Programas que cruzaron: {cruzaron}")
            print(f"Programas que NO cruzaron: {no_cruzaron}")
        
        # Guardar resultado como atributo de instancia
        self.data = Programas_EFT

    def validar_datos(self, df):
        """
        Realiza validaciones generales sobre el dataframe de entrada.

        Parameters:
        - df (pd.DataFrame): Datos de entrada para validar.
        """
        pass
        
    def crear_rutas(self, nombre_archivo_habilitados, nombre_archivo_complementario=None):
        """
        Crea un diccionario que contiene un DataFrame para cada ruta habilitada.
    
        Esta función carga los datos desde los archivos especificados y luego separa
        la información en distintos DataFrames, uno por cada valor único en la columna 
        'Ruta habilitada'. Cada DataFrame se guarda en un diccionario con la ruta como clave.
    
        Parámetros:
            nombre_archivo_habilitados (str): Nombre o ruta del archivo principal con los datos habilitados.
            nombre_archivo_complementario (str, opcional): Nombre o ruta del archivo complementario 
                con información adicional (por defecto es None).
    
        Retorna:
            dict: Un diccionario donde las claves son los nombres de las rutas habilitadas y 
            los valores son los DataFrames correspondientes a cada ruta.
        """
        self.__cargar_datos_crudos(nombre_archivo_habilitados, nombre_archivo_complementario)
        
        ruta_labels = self.data['Ruta habilitada'].unique()

        # Crear un diccionario con un DataFrame por cada valor de ruta
        rutas_dict = {
            ruta: self.data.loc[self.data['Ruta habilitada'] == ruta].copy()
            for ruta in ruta_labels
        }
        
        return rutas_dict 

    def calcular_distribucion(self):
        """
        Ejecuta la lógica genérica de distribución de recursos de TODAS las rutas.
        """
        pass

    def exportar_resultado(self, path_salida):
        """
        Exporta el resultado de la asignación a un archivo.

        Parameters:
        - path_salida (str): Ruta del archivo de salida.
        """
        pass


# In[4]:


rutas = AsignacionBase().crear_rutas("Habilitados final 26052025.xlsx","Base final - Oferta Activa.pkl")


# ### Clase asignacion Nuevos - Antiguos

# In[5]:


class AsignacionNuevosAntiguos(AsignacionBase):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase con los métodos para gestionar la asignación de recursos para la ruta 'Antiguos' o 'Nuevos'.
    """
    
    def __init__(self, data, nombre_ruta):
        """
        TO DO: Descripcion

        Parameters:
        - data (pandas dataframe): Dataframe con la inforamcion de los programas Antiguos
        - nombre_ruta: el nombre de la ruta como se especifica en las llaves de constants_robusto.RECURSOS_POR_RUTA
        """
        
        super().__init__(RECURSOS_POR_RUTA[nombre_ruta])
        self.data = data
        
    def _ponderar_ipo(self, alfa = 1, ponderar = True):
        """
        Calcula un IPO ponderado como (IPO^alfa) * cupos, si `ponderar` es True.
    
        Parámetros:
        - alfa (float): Exponente aplicado al IPO (≥ 1).
        - ponderar (bool): Si False, no se pondera por cupos.
    
        Crea la columna 'ipo_ponderado' en el DataFrame self.data.
        """
    
        # Validación del parámetro alfa
        if not isinstance(alfa, (int, float)):
            raise TypeError("El parámetro 'alfa' debe ser un número.")
        if alfa < 1:
            raise ValueError("El parámetro 'alfa' debe ser mayor o igual a 1.")
        
        if ponderar:
            self.data['ipo_ponderado'] = self.data['numero_cupos_ofertar'] * (self.data['IPO'] ** alfa)
        else:
            alfa = 1
            beta = 0
            self.data['ipo_ponderado'] = (self.data['numero_cupos_ofertar']**beta) * (self.data['IPO'] ** alfa)


    def calcular_recursos_por_cno(self, alfa=1, ponderar=True, group=['cod_CNO']):
        """
        
        Calcula y distribuye recursos por grupo ocupacional (CNO) según el IPO ponderado.
    
        Aplica una ponderación al IPO, agrupa los datos por las columnas especificadas en `group`,
        calcula la participación relativa de cada grupo en el total ponderado y asigna recursos
        proporcionalmente.
    
        Parámetros:
        ----------
        alfa : float, opcional (default=1)
            Exponente para ponderar el IPO. Debe ser ≥ 1.
        ponderar : bool, opcional (default=True)
            Indica si se pondera el IPO por número de cupos ofertados.
        group : list[str], opcional (default=['cod_CNO'])
            Columnas por las que se agrupan los datos.
    
        Retorna:
        -------
        pd.DataFrame
            DataFrame con recursos asignados por grupo, incluyendo columnas: 'recursosxcno',
            y 'n_programas'.
        """
        self._ponderar_ipo(alfa=alfa, ponderar=ponderar)
    
        # Calcular total de IPO ponderado
        ipo_ponderado_total = self.data['ipo_ponderado'].sum()
    
        # Agrupar datos por CNO y calcular métricas
        grouped = (
            self.data
            .groupby(group)
            .agg(
                ipo_ponderado=('ipo_ponderado', 'sum'),
                CUPOS=('numero_cupos_ofertar', 'sum'),
                IPO=('IPO', 'sum'),
                n_programas=('ipo_ponderado', 'count')
            )
            .reset_index()
        )
    
        # Calcular participación relativa y asignar recursos
        grouped['participacion_ipo'] = grouped['ipo_ponderado'] / ipo_ponderado_total
        grouped['recursosxcno'] = grouped['participacion_ipo'] * self.recursos_disponibles
    
        # Seleccionar columnas finales
        result = grouped[group + ['recursosxcno', 'n_programas']]
    
        # Agregar columna de recursos al DataFrame original
        self.data = self.data.merge(
            grouped[group + ['recursosxcno']],
            on=group,
            how='left'
        )
    
        return result
        


# In[6]:


df_antiguos = rutas['Antiguos']
instancia_nuevos_antiguos = AsignacionNuevosAntiguos(df_antiguos, "antiguos")
recursosxcno = instancia_nuevos_antiguos.calcular_recursos_por_cno()


# ### Clase asignacion Antiguos

# In[35]:


class AsignacionAntiguos(AsignacionNuevosAntiguos):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Antiguos'.
    """

    def __init__(self, data):
        """
        Inicializa la asignación con los recursos disponibles específicos para la ruta antiguos.

        Parameters:
        - data (pandas dataframe): Dataframe con la inforamcion de los programas Antiguos
        """
        super().__init__(data, "antiguos")
        #TODO: Definir contrato
        self.data = data
        
        #Atributos para guardar los recursos de la primera y segunda asignacion de recursos
        self.primera_asignacion = None
        self.segunda_asignacion = None

        self.columnas_exportar = [
            'cod_CNO',
            'Ocupación',
            'IPO',
            'ISOEFT_4d',
            'CODIGO_INSTITUCION',
            'CODIGO_PROGRAMA',
            'recursosxcno', 
            'numero_cupos_ofertar',
            'cupos_asignados_2E',
            'recurso_asignado_2E',
            'cupos_asignados_3E',
            'recurso_asignado_3E',
            'Total_Cupos_Asignados',
            "Saldo_Remanente_3E"
        ]
        
        #Garantiza que al instanciar la clase, se calculen inmediatamente los recursos por cno.
        self.calcular_recursos_por_cno()
        #Ordenamos por ISOEFT (condición necesaria para la asignacion de recursos)
        self.ordenar_ocupaciones_por_isoeft()
        #Garantiza que al instanciar la clase, se calcule la segunda asignacion e implicitamente la primera asignacion
        self.asignar_recursos_segunda_etapa()

    def ordenar_ocupaciones_por_isoeft(self):
        """
        ## TODO: Eliminar la posibilidad de que hayan NANS. Esto se debe corregir desde la fuente
        
        Ordena un DataFrame por ['cod_CNO', 'Ocupación', 'IPO', 'ISOEFT_4d'],
        asegurando que las filas con NaN en 'ISOEFT_4d' queden al final del DataFrame completo.

        """
        # Separar por presencia de NaN en ISOEFT_4d
        sin_nan = self.data[self.data['ISOEFT_4d'].notna()]
        con_nan = self.data[self.data['ISOEFT_4d'].isna()]
    
        #Columnas para ordenar
        columnas = [
            'IPO',
            'cod_CNO',
            'Ocupación',
            'ISOEFT_4d',
            COLUMNA_VALOR_PROGRAMA,
            "numero_cupos_ofertar",
            "duracion_horas_programa"
        ]
    
        orden = [
            False,
            True,
            True,
            False,
            True,
            False,
            True
        ]
        
        # Ordenar las filas válidas
        sin_nan = sin_nan.sort_values(
            columnas, 
            ascending= orden
        )
    
        # Concatenar
        self.data = pd.concat([sin_nan, con_nan], ignore_index=True)

    def asignar_recursos_primera_etapa(self):
        """
        Asigna cupos y recursos por ocupación según los lineamientos de la Ruta Antiguos, paso 2
    
        Retorna un resumen por ocupación con cupos y recursos asignados, y los saldos no utilizados.
        """       
        data = self.data.copy()
        # Paso 1: Crear nueva columna para asignación
        data['cupos_asignados_2E'] = 0
    
        # Paso 2: Iterar por grupo de ocupación para asignar los recursos disponibles
        for (cod_cno, Ocupación), grupo in data.groupby(['cod_CNO', 'Ocupación']):
            recurso_por_dispersar = grupo['recursosxcno'].iloc[0]
            saldo = recurso_por_dispersar
            indices = grupo.index
    
            for i in indices:
                costo_unitario = data.loc[i, COLUMNA_VALOR_PROGRAMA]
                cupos_disp = data.loc[i, 'numero_cupos_ofertar']

                ## TODO: Esta condicion deberia verificarse desde la fuente
                if pd.isna(costo_unitario) or costo_unitario == 0:
                    continue
    
                recurso_necesario = cupos_disp * costo_unitario
    
                if saldo >= recurso_necesario:
                    data.loc[i, 'cupos_asignados_2E'] = cupos_disp
                    saldo -= recurso_necesario
                else:
                    # Ver si se puede financiar al menos un cupo
                    cupos_asignables = saldo // costo_unitario
                    data.loc[i, 'cupos_asignados_2E'] = cupos_asignables
                    saldo -= cupos_asignables * costo_unitario
                    break
    
        # Paso 3: Calcular recursos efectivamente asignados por programa
        data['recurso_asignado_2E'] = data['cupos_asignados_2E'] * data[COLUMNA_VALOR_PROGRAMA]
    
        # Paso 4: Agrupar para obtener resumen de asignaciones por Ocupación
        asignacion_por_ocupacion_ant = data.groupby(['cod_CNO', 'Ocupación']).agg(
            recurso_asignado_2E=('recurso_asignado_2E', 'sum'),
            cupos_asignados_2E=('cupos_asignados_2E', 'sum')
        ).reset_index()
    
        # Paso 5: Obtener recursos originales y número de cupos ofertados por las instituciones
        recursos_por_ocupacion = data.groupby(['cod_CNO', 'Ocupación']).agg(
            recursosxcno=('recursosxcno', 'first'),
            numero_cupos_ofertar=('numero_cupos_ofertar', 'sum')
        ).reset_index()
    
        # Paso 6: Unir ambas tablas
        asignacion_por_ocupacion_ant = asignacion_por_ocupacion_ant.merge(
            recursos_por_ocupacion, on=['cod_CNO', 'Ocupación']
        )
    
        # Paso 7: Calcular saldos no asignados
        asignacion_por_ocupacion_ant['Saldo_No_Asignado_2E'] = (
            asignacion_por_ocupacion_ant['recursosxcno'] - asignacion_por_ocupacion_ant['recurso_asignado_2E']
        )
    
        asignacion_por_ocupacion_ant['cupos_no_asignados_2E'] = (
            asignacion_por_ocupacion_ant['numero_cupos_ofertar'] - asignacion_por_ocupacion_ant['cupos_asignados_2E']
        )

        self.primera_asignacion = data
        
        return asignacion_por_ocupacion_ant
        
    def asignar_recursos_segunda_etapa(self):
        """
        Asigna recursos sobrantes de la segunda etapa a programas priorizados en una tercera etapa,
        usando una bolsa común. Actualiza el DataFrame original con asignaciones adicionales.
        """
        
        asignacion_por_ocupacion = self.asignar_recursos_primera_etapa()
        
        saldo_comun_3E = asignacion_por_ocupacion['Saldo_No_Asignado_2E'].sum()
        
        data = self.primera_asignacion.copy()
        
        data['cupos_asignados_3E'] = 0
        data['recurso_asignado_3E'] = 0.0
        
        #TODO: verificar si esta condicion es redundante | acondicionarla para la clase
        #      data = ordenar_ocupaciones_por_isoeft(data)
    
        for idx, row in data.iterrows():
            costo = row[COLUMNA_VALOR_PROGRAMA]
            cupos = row['numero_cupos_ofertar']
            if pd.isna(costo) or costo <= 0 or pd.isna(cupos) or cupos <= 0:
                continue
    
            recurso_necesario = costo * cupos
            
            if saldo_comun_3E >= recurso_necesario:
                data.at[idx, 'cupos_asignados_3E'] = cupos
                data.at[idx, 'recurso_asignado_3E'] = recurso_necesario
                saldo_comun_3E -= recurso_necesario
            else:
                cupos_posibles = saldo_comun_3E // costo
                if cupos_posibles >= 1:
                    recurso_asignado = cupos_posibles * costo
                    data.at[idx, 'cupos_asignados_3E'] = cupos_posibles
                    data.at[idx, 'recurso_asignado_3E'] = recurso_asignado
                    saldo_comun_3E -= recurso_asignado
                else:
                    break
    
        data['Total_Cupos_Asignados'] = data['cupos_asignados_2E'] + data['cupos_asignados_3E']
        data['Total_Recurso_Asignado'] = data['recurso_asignado_2E'] + data['recurso_asignado_3E']
        data['Saldo_Remanente_3E'] = saldo_comun_3E
        
        self.segunda_asignacion = data    
        
    def validar_datos_antiguos(self):
        """
        Valida las pre-condiciones específicas para los datos de programas antiguos.
        """
        pass



# In[36]:


instancia_antiguos = AsignacionAntiguos(df_antiguos)


# ### Clase asignación Nuevos

# In[ ]:


class AsignacionNuevos(AsignacionNuevosAntiguos):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Viejos'.
    """

    def __init__(self):
        super().__init__(RECURSOS_POR_RUTA["nuevos"])

    def preparar_datos_nuevos(self):
        """
        Aplica reglas y filtros específicos para programas 'Viejos'.
        """
        pass

    def asignar_recursos_nuevos(self):
        """
        Implementa la lógica de asignación de recursos específica para la ruta 'Viejos'.
        """
        pass


# ### Clase asignación Cerrados

# In[ ]:


class AsignacionCerrados(AsignacionBase):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Cerrados'.
    """

    def __init__(self):
        super().__init__(RECURSOS_POR_RUTA["cerrados"])

    def preparar_datos_cerrados(self):
        """
        Aplica reglas y filtros específicos para programas cerrados.
        """
        pass

    def asignar_recursos_cerrados(self):
        """
        Implementa la lógica de asignación de recursos específica para la ruta 'Cerrados'.
        """
        pass


# In[3]:


get_ipython().system('jupyter nbconvert --to script temp_clase_asignacion.ipynb --output temp_clase_asignacion')


# In[ ]:




