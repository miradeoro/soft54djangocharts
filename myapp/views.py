from django.shortcuts import render

# Create your views here.

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse


import json

import datetime

import pyodbc
import pandas as pd
import time
import sys
import datetime

from sqlalchemy import create_engine


#params demo
FechaInicio="07/01/2019"
CuitCliente="38614672"


def informix_query(query:str):
    #print(query)     
    #start=time.perf_counter()
    
    #conexion Informix
    informix_database="informix"
    #TEST!
    #informix_database="trumar"
    conn_str="DSN=informix64;UID=informix;PWD=INFORMIX;Database="+informix_database
    
    try:
        conn = pyodbc.connect(conn_str)
        #cursor = conn.cursor()
        
        # Convert your ODBC connection string to an SQLAlchemy URL format
        #conn_str = "informix://informix:INFORMIX@informix64/informix?driver=IBM+INFORMIX+ODBC+DRIVER+(64-bit)"

        # Create an SQLAlchemy engine
        #engine = create_engine(conn_str)

        # Use the engine with pandas
        #cursor.execute(query)
        data = pd.read_sql(query, conn)

        # Fetch all data
        #data = cursor.fetchall()

        # Fetch columns names
        #columns = [column[0] for column in cursor.description]

    except Exception as e:
        print(f"An error occurred: {e}")
        data = []
        columns = []

    #finally:
        # Close the cursor and connection if they were successfully opened
        # if cursor:
        #     cursor.close()
        # if conn:
        #     conn.close()
        #engine.dispose()

   
    
    #data = pd.DataFrame(data, columns=columns)
    #print(df.head())


    #stop=time.perf_counter()
    #print(f"Me tomo: {stop-start:.2f} segs")
    return data


#formato Argy a formato Informix
def convert_date_format(date_string):
    date_object = datetime.datetime.strptime(date_string, '%d/%m/%Y')
    return date_object.strftime('%m/%d/%Y')

def vet_get_puntos_disponibles(cuit:str):

    #Puntos Acumulados         
    selecttext = "SELECT vetoaa.dat_nrocuit,"
    selecttext += "round(sum(vetoaa.imp_total * vetoaa.dat_signo )* 0.02) AS Puntos "
    selecttext += "FROM vetoaa "
    selecttext += "WHERE dat_tipcon = 'zzz' "
    selecttext += "AND fec_fechacompro >='"+FechaInicio+"' "  
    selecttext += "AND vetoaa.dat_nrocuit='" + cuit + "' " 
    selecttext += "GROUP BY vetoaa.dat_nrocuit"

    resultado=informix_query(selecttext)

    try:
        resultado=int(resultado['puntos'].values[0])
        
    except:
       resultado=0
    
    return resultado


def vet_get_puntos_utilizados(cuit:str):
    #Puntos Utilizados
    selecttext2 = "SELECT vetoaa.dat_nrocuit,"
    selecttext2 += "round(sum(stmsaa.imp_importe * stmsaa.dat_signo*stmsaa.imp_paripeso)) AS Importe,"
    selecttext2 += "TO_CHAR(MAX(vetoaa.fec_fechacompro),'%Y%m%d')" 
    selecttext2 += " FROM vetoaa, stmsaa "
    selecttext2 += " WHERE dat_tipcon = 'zzz' "
    selecttext2 += " AND vetoaa.cod_comprobante =stmsaa.cod_comproorig" 
    selecttext2 += " AND vetoaa.dat_numerodesde =stmsaa.nro_comproorig "
    selecttext2 += " AND fec_fechacompro = fec_registracion" 
    selecttext2 += " AND cod_su_sucursal = cod_sucursal" 
    selecttext2 += " AND cod_ce_empresa = cod_empresa" 
    selecttext2 += " AND STMSAA.COD_PRODUCTO = '9999-9989' " 
    selecttext2 += " AND vetoaa.dat_nrocuit='" + cuit + "'" 
    selecttext2 += " AND fec_fechacompro >='" + FechaInicio + "' " 
    selecttext2 += " GROUP BY vetoaa.dat_nrocuit"
    
   

    resultado=informix_query(selecttext2)

    try:
        Puntos_Utilizados=resultado['importe'].values[0]
        
    except:
        Puntos_Utilizados=0
    
    return Puntos_Utilizados

    
   
#views start here           
def search(request):
    return render(request, 'search.html')

def puntos(request):
    query = request.GET.get('dni')
    #traer puntos de la base
    puntos_disponibles=vet_get_puntos_disponibles(cuit=query)
    #puntos_disponibles=int(puntos_disponibles['puntos'])

    #puntos utilizados
    puntos_utilizados=vet_get_puntos_utilizados(cuit=query)
    
    #formula A*0.02-B
    #puntos_formula=0

    try:
        puntos_formula=int(puntos_disponibles)-int(puntos_utilizados)
    except:
        puntos_formula=0


    
    #Fecha de hoy
    hoy = datetime.date.today()
    hoy_formateado = hoy.strftime('%d-%m-%Y')

    return render(request, 'puntos.html', {
        'query': query,
        'puntos_disponibles':puntos_disponibles,
        'puntos_utilizados':puntos_utilizados,
        'puntos_formula':puntos_formula,
        'hoy_formateado':hoy_formateado
        }
        )

def chart_home(request):
    #sales = Sales.objects.all()

    #labels = [sale.date for sale in sales]
    #data = [sale.amount for sale in sales]

    # labels=["Enero","Febrero","Marzo","Abril","Mayo"]
    # data=[210,313,321,124,512]
    
    # return render(request, 'grafico.html', {
    #     'labels': json.dumps(labels, cls=DjangoJSONEncoder),
    #     'data': json.dumps(data, cls=DjangoJSONEncoder),
    # })
    return render(request, 'grafico_charthome.html')


def get_vtaxvend_data(request):

    FechaDesde="07/12/2023"
    FechaHasta="07/23/2023"

    desde = request.GET.get('from_date')  # Get the "desde" date from the query parameters
    hasta = request.GET.get('to_date')  # Get the "hasta" date from the query parameters


    FechaDesde=str(desde)
    FechaHasta=str(hasta)
    
    print(type(desde))
    print(desde)

    
    FechaDesde=convert_date_format(desde)
    FechaHasta=convert_date_format(hasta) 
    

    selecttext = "SELECT VEVEAA.dat_nombre AS Vend, SUM(IMP_TOTAL*DAT_SIGNO*IMP_PARIPESO) AS Total FROM VETOAA"
    selecttext += " INNER JOIN VEVEAA on cod_codigo=cod_vendedor"
    selecttext += " WHERE dat_tipcon='zzz' and (VETOAA.fec_fechacompro>='"+ FechaDesde +"' and VETOAA.fec_fechacompro<='"+FechaHasta+"')"
    selecttext += " and dat_vercam=1"
    selecttext += " GROUP BY dat_nombre"

    resultado=informix_query(selecttext)

    try:
        print(resultado)
        #VtaxVendedor=resultado['Vend'].values[0]
        #labels=["Enero","Febrero","Marzo","Abril","Mayo"]
        #data=[210,313,321,124,512]
        labels=resultado['vend'].values.tolist()
        data=resultado['total'].values.tolist()

    except:
        labels=[]
        data=[]

   
    
    return JsonResponse({
        'labels': labels,
        'data': data,
    })
              
def get_vtaxperiodo_data(request):

    FechaDesde="06/01/2023"
    FechaHasta="07/23/2023"

    desde = request.GET.get('from_date')  # Get the "desde" date from the query parameters
    hasta = request.GET.get('to_date')  # Get the "hasta" date from the query parameters
    empresa_elegida=request.GET.get('empresa_seleccionada')

    FechaDesde=str(desde)
    FechaHasta=str(hasta)
    
    #print(type(desde))
    #print(desde)
    print(empresa_elegida)

    
    FechaDesde=convert_date_format(desde)
    FechaHasta=convert_date_format(hasta) 
    

    selecttext = "SELECT  YEAR(fec_fechacompro)||'/'||LPAD(MONTH(fec_fechacompro),2,'0')  AS MesAno, SUM(VETOAA.imp_total*VETOAA.dat_signo*VETOAA.imp_paripeso) AS Total"
    selecttext += " FROM VETOAA"
    selecttext += " WHERE dat_tipcon='zzz' and (VETOAA.fec_fechacompro>='"+ FechaDesde  +"' and VETOAA.fec_fechacompro<='"+FechaHasta+"')"
    selecttext += " and VETOAA.cod_empresa='"+empresa_elegida+"'"
    selecttext += " GROUP BY  1"
    selecttext += " ORDER BY 1"

    resultado=informix_query(selecttext)

    try:
        print(resultado)
        labels=resultado['mesano'].values.tolist()
        data=resultado['total'].values.tolist()

    except:
        labels=[]
        data=[]

   
    return JsonResponse({
        'labels': labels,
        'data': data,
    })

def get_vtaxdia_data(request):

    FechaDesde="06/01/2023"
    FechaHasta="07/23/2023"

    desde = request.GET.get('from_date')  # Get the "desde" date from the query parameters
    hasta = request.GET.get('to_date')  # Get the "hasta" date from the query parameters


    FechaDesde=str(desde)
    FechaHasta=str(hasta)
    
    FechaDesde=convert_date_format(desde)
    FechaHasta=convert_date_format(hasta) 
    

    selecttext = "SELECT  VETOAA.fec_fechacompro as Fecha, sum(VETOAA.imp_total*VETOAA.dat_signo*VETOAA.imp_paripeso) AS Importe"
    selecttext += " FROM VETOAA"
    selecttext += " WHERE dat_tipcon='zzz' and (VETOAA.fec_fechacompro>='"+ FechaDesde  +"' and VETOAA.fec_fechacompro<='"+FechaHasta+"')"
    selecttext += " GROUP BY VETOAA.fec_fechacompro"
    selecttext += " ORDER BY 1"

    resultado=informix_query(selecttext)

    try:
        print(resultado)
        labels=resultado['fecha'].values.tolist()
        data=resultado['importe'].values.tolist()
    

    except:
        labels=[]
        data=[]

   
    return JsonResponse({
        'labels': labels,
        'data': data,
    })

def get_empresas_data(request):

    # Trae cada sub empresa del cliente

    selecttext = "SELECT cod_ce_empresa,dat_ce_razonsocial FROM  GZEMAA"
    

    resultado=informix_query(selecttext)
    #print(resultado)

    try:
        #print(resultado)
        #opcion TODAS
        empresa=["TODAS"]
        
        cod_empresa=resultado['cod_ce_empresa'].values.tolist()
        resultado=resultado['dat_ce_razonsocial'].values.tolist()

        for emp in resultado:
            empresa.append(emp)
        

    except:
        empresa=[]
        cod_empresa=[]
     
    return JsonResponse({
        'empresa': empresa,
        'codigo_empresa': cod_empresa,
        
        
    })


def get_sucursales_data(request):

    # Trae cada sucursal del cliente
    #To do :Empresa=GET etc
    
    empresa_elegida=request.GET.get('empresa_seleccionada')

    print(empresa_elegida)
    selecttext = "SELECT GZSUAA.nro_sucursal,DAT_EMPRESA FROM GZSUAA"
    selecttext +=" INNER JOIN GZEMAA on GZSUAA.cod_ce_empresa=GZEMAA.cod_ce_empresa "
    selecttext +=" WHERE GZEMAA.cod_ce_empresa='"+empresa_elegida+"' and GZSUAA.dat_vercam='1'"
    

    resultado=informix_query(selecttext)

    try:
        print(resultado)
        #sucursal=["TODAS"]
        sucursal=resultado['dat_empresa'].values.tolist()
        
        #nro_sucursal=["TODAS"]   
        #nro_sucursal=nro_sucursal.append(resultado['nro_sucursal'].values.tolist())
    except:
        sucursal=[]
        #nro_sucursal=[]
        
    print("sucu",sucursal)
    return JsonResponse({
        #'numero_sucursal': nro_sucursal,
        'sucursal': sucursal,
        
    })



def get_listadosaldos_data_vendedores(request):

    # Pide de cliente a cliente y de vendedor a vendedor (por default vienen el primero y último de la tabla de los 2) 
    # Tabla:VEDEAA  VEVEAA (tiene cod_codigo y dat_nombre)

    # El listado es Código Cliente - Razon Social - Saldo

    # Recorre el VEDEAA (es el archivo de deuda pendiente)
    # Codigo=Cod_cliente
    # Razon social= lee el veclaa con el cod_cliente
    # Saldo=sum(dat_sigo*dat_saldo) (de ese cliente)

    # Filtra vendedor (cod_vendedor)
    # Esta parte trae los vendedores


    selecttext = "SELECT * FROM VEVEAA"
    selecttext += " WHERE DAT_VERCAM=1"
    

    resultado=informix_query(selecttext)

    try:
        #print(resultado)
        codigo=resultado['cod_codigo'].values.tolist()
        vendedor=resultado['dat_nombre'].values.tolist()
        

    except:
        codigo=[]
        vendedor=[]
     
    return JsonResponse({
        #'codigo': codigo,
        'vendedor': vendedor,
        
    })

def get_listadosaldos_data_clientes(request):

    # Pide de cliente a cliente y de vendedor a vendedor (por default vienen el primero y último de la tabla de los 2) 
    # Tabla:VEDEAA  VEVEAA (tiene cod_codigo y dat_nombre)

    # El listado es Código Cliente - Razon Social - Saldo

    # Recorre el VEDEAA (es el archivo de deuda pendiente)
    # Codigo=Cod_cliente
    # Razon social= lee el veclaa con el cod_cliente
    # Saldo=sum(dat_sigo*dat_saldo) (de ese cliente)

    # Filtra vendedor (cod_vendedor)
    # Esta parte trae el primer y ultimo cliente de la tabla


    #primer cliente
    selecttext = "SELECT FIRST 1 * FROM VEDEAA"
    selecttext += " ORDER BY COD_CLIENTE"

    resultado=informix_query(selecttext)

    try:
        #print(resultado)
        primer_cliente=resultado['cod_cliente'].values.tolist()

    except:
        primer_cliente=[]
    
    #ultimo  cliente
    selecttext = "SELECT FIRST 1 * FROM VEDEAA"
    selecttext += " ORDER BY COD_CLIENTE DESC"

    resultado=informix_query(selecttext)

    try:
        #print(resultado)
        ultimo_cliente=resultado['cod_cliente'].values.tolist()
        
    except:
        ultimo_cliente=[]
    
     
    return JsonResponse({
    
        'primercliente': primer_cliente,
        'ultimocliente': ultimo_cliente,
        
        
    })


def get_rankingxcliente_data(request):

    #teest
    FechaDesde="06/01/2023"
    FechaHasta="07/23/2023"

    desde = request.GET.get('from_date')
    hasta = request.GET.get('to_date')  

    #limit
    limite=request.GET.get('top_registros')  

    if limite==None or limite==0:
        limite=50

    FechaDesde=str(desde)
    FechaHasta=str(hasta)
    
    
    FechaDesde=convert_date_format(desde)
    FechaHasta=convert_date_format(hasta)

    # Filtra vendedor (cod_vendedor)
    vendedor_param = request.GET.get('vendedor_seleccionado')
    #vendedor_param="TODOS"
    
    

    #TODOS los vendedores o uno especifico
    if vendedor_param=="TODOS":
        
        selecttext = "SELECT FIRST "+limite+" COD_CLIENTE,DAT_RAZONSOCIAL,SUM(IMP_TOTAL*DAT_SIGNO*IMP_PARIPESO) AS FACTURADO"
        selecttext += " FROM VETOAA"
        selecttext += " JOIN veveaa on veveaa.cod_codigo=VETOAA.cod_vendedor"
        selecttext += " WHERE dat_tipcon='zzz' and (VETOAA.fec_fechacompro>='"+ FechaDesde  +"' and VETOAA.fec_fechacompro<='"+FechaHasta+"')"
        selecttext += " GROUP BY 1,2"
        selecttext += " ORDER BY 3 DESC"


    else:     
        selecttext = "SELECT FIRST "+limite+" COD_CLIENTE,DAT_RAZONSOCIAL,SUM(IMP_TOTAL*DAT_SIGNO*IMP_PARIPESO) AS FACTURADO"
        selecttext += " FROM VETOAA"
        selecttext += " JOIN veveaa on veveaa.cod_codigo=VETOAA.cod_vendedor"
        selecttext += " WHERE dat_tipcon='zzz' and (VETOAA.fec_fechacompro>='"+ FechaDesde  +"' and VETOAA.fec_fechacompro<='"+FechaHasta+"')"
        selecttext += " AND veveaa.dat_nombre='"+str(vendedor_param)+"'"
        selecttext += " GROUP BY 1,2"
        selecttext += " ORDER BY 3 DESC"




    resultado=informix_query(selecttext)

    try:
        #filtrar saldos 0
        #resultado=resultado[resultado['saldo']!=0]
        print(resultado)
        codigo=resultado['cod_cliente'].values.tolist()
        razon_social=resultado['dat_razonsocial'].values.tolist()
        facturacion=resultado['facturado'].values.tolist()

    except:
        codigo=[]
        razon_social=[]
        facturacion=[]

    #demo!
    #labels=["Enero","Febrero","Marzo","Abril","Mayo"]
    #data=[210,313,321,124,512]
    #print(codigo)
    #print(razon_social)
    #print(saldo)

    data={
        'codigo': codigo,
        'razonsocial': razon_social,
        'facturacion': facturacion,
    }
    
   
    return JsonResponse(data)


def get_listadosaldos_data(request):

    
    #FechaDesde=convert_date_format(desde)
    #FechaHasta=convert_date_format(hasta) 
    
    # Pide de cliente a cliente y de vendedor a vendedor (por default vienen el primero y último de la tabla de los 2) 
    # Tabla:VEDEAA  VEVEAA (tiene cod_codigo y dat_nombre)

    # El listado es Código Cliente - Razon Social - Saldo

    # Recorre el VEDEAA (es el archivo de deuda pendiente)
    # Codigo=Cod_cliente
    # Razon social= lee el veclaa con el cod_cliente
    # Saldo=sum(dat_sigo*dat_saldo) (de ese cliente)
    
    #3 meses a la fecha
    desde= datetime.date.today()

    #Calcular 3 meses para atras teniendo cuidado que el dia exista
    year = desde.year
    month = desde.month - 3

    # If the month goes below 1, adjust the year and month accordingly
    if month <= 0:
        year -= 1
        month += 12

    try:
        # Attempt to create the date 3 months ago
        three_months_ago = datetime.date(year, month, desde.day)
    except ValueError:
        # This block will be executed if today's day doesn't exist in the target month 
        # (e.g., today is Jan 31, and we're trying to find Oct 31 which doesn't exist)
        # In such case, find the last day of the target month
        while month > 0:
            month -= 1
            try:
                three_months_ago = datetime.date(year, month+1, desde.day)
                break
            except ValueError:
                continue

    hasta=three_months_ago

    desde = desde.strftime("%m/%d/%Y")
    hasta = hasta.strftime("%m/%d/%Y")

    FechaDesde=str(desde)
    FechaHasta=str(hasta)

    #FechaDesde=convert_date_format(desde)
    #FechaHasta=convert_date_format(hasta)
    
    #print(type(desde))
    
    # Filtra vendedor (cod_vendedor)
    vendedor_param = request.GET.get('vendedor_seleccionado')

    cliente_desde=request.GET.get('cliente_desde')
    cliente_hasta=request.GET.get('cliente_hasta')

    
    #valores demo para trumar
    #cliente_desde="35"
    #cliente_hasta="170"

    #TODOS los vendedores o uno especifico
    if vendedor_param=="TODOS":
        selecttext = "SELECT vedeaa.cod_cliente as Codigo,"
        selecttext += "veclaa.dat_razonsocial as RazonSocial,veclaa.cod_vendedor as Vendedor,"
        selecttext += "veveaa.dat_nombre as NombreVendedor,"
        selecttext += "sum(vedeaa.dat_signo*vedeaa.dat_saldo*vedeaa.imp_paripeso) as Saldo"
        selecttext += " FROM vedeaa"
        selecttext += " JOIN veclaa on vedeaa.cod_cliente=veclaa.cod_codigo"
        selecttext += " JOIN veveaa on veveaa.cod_codigo=veclaa.cod_vendedor"
        selecttext += " WHERE (vedeaa.cod_cliente>="+cliente_desde+" and vedeaa.cod_cliente<="+cliente_hasta+")"
        selecttext += " AND veclaa.dat_vercam=1"
        selecttext += " AND vedeaa.fec_fechacompro>="+FechaDesde
        selecttext += " AND vedeaa.fec_fechacompro>="+FechaHasta
        selecttext += " GROUP BY 1,2,3,4"
        selecttext += " ORDER BY Codigo,Saldo"
        #  #filtrar saldos en 0
        # selecttext = "SELECT"
        # selecttext += " subquery.Codigo,"
        # selecttext += "subquery.RazonSocial,"
        # selecttext += "subquery.Vendedor,"
        # selecttext += "subquery.NombreVendedor,"
        # selecttext += "subquery.Saldo"
        # selecttext += " FROM ("
        # selecttext += "    SELECT"
        # selecttext += "  vedeaa.cod_cliente AS Codigo,"
        # selecttext += "veclaa.dat_razonsocial AS RazonSocial,"
        # selecttext += "veclaa.cod_vendedor AS Vendedor,"
        # selecttext += "veveaa.dat_nombre AS NombreVendedor,"
        # selecttext += "SUM(vedeaa.dat_signo * vedeaa.dat_saldo) AS Saldo"
        # selecttext += " FROM" 
        # selecttext += " vedeaa"
        # selecttext += " JOIN"
        # selecttext += " veclaa ON vedeaa.cod_cliente = veclaa.cod_codigo"
        # selecttext += " JOIN"
        # selecttext += " veveaa ON veveaa.cod_codigo = veclaa.cod_vendedor"
        # selecttext += " WHERE"
        # selecttext += " (vedeaa.cod_cliente>="+cliente_desde+" and vedeaa.cod_cliente<="+cliente_hasta+")"
        # selecttext += " AND veclaa.dat_vercam=1"
        # selecttext += " GROUP BY"
        # selecttext += " 1, 2, 3, 4"
        # selecttext += ") AS subquery"
        # selecttext += " WHERE"
        # selecttext += " subquery.Saldo <> 0"
        # selecttext += " ORDER BY"
        # selecttext += " subquery.Saldo"

    else:     
        selecttext = "SELECT vedeaa.cod_cliente as Codigo,"
        selecttext += "veclaa.dat_razonsocial as RazonSocial,veclaa.cod_vendedor as Vendedor,"
        selecttext += "veveaa.dat_nombre as NombreVendedor,"
        selecttext += "sum(vedeaa.dat_signo*vedeaa.dat_saldo*vedeaa.imp_paripeso) as Saldo"
        selecttext += " FROM vedeaa"
        selecttext += " JOIN veclaa on vedeaa.cod_cliente=veclaa.cod_codigo"
        selecttext += " JOIN veveaa on veveaa.cod_codigo=veclaa.cod_vendedor"
        selecttext += " WHERE veveaa.dat_nombre='"+str(vendedor_param)+"'"
        selecttext += " AND (vedeaa.cod_cliente>="+cliente_desde+" and vedeaa.cod_cliente<="+cliente_hasta+")"
        selecttext += " AND veclaa.dat_vercam=1"
        selecttext += " AND vedeaa.fec_fechacompro>="+FechaDesde
        selecttext += " AND vedeaa.fec_fechacompro>="+FechaHasta
        selecttext += " GROUP BY 1,2,3,4"
        selecttext += " ORDER BY Codigo,Saldo"

        #filtrar saldos en 0
        # selecttext = "SELECT"
        # selecttext += " subquery.Codigo,"
        # selecttext += "subquery.RazonSocial,"
        # selecttext += "subquery.Vendedor,"
        # selecttext += "subquery.NombreVendedor,"
        # selecttext += "subquery.Saldo"
        # selecttext += " FROM ("
        # selecttext += "    SELECT"
        # selecttext += "  vedeaa.cod_cliente AS Codigo,"
        # selecttext += "veclaa.dat_razonsocial AS RazonSocial,"
        # selecttext += "veclaa.cod_vendedor AS Vendedor,"
        # selecttext += "veveaa.dat_nombre AS NombreVendedor,"
        # selecttext += "SUM(vedeaa.dat_signo * vedeaa.dat_saldo) AS Saldo"
        # selecttext += " FROM" 
        # selecttext += " vedeaa"
        # selecttext += " JOIN"
        # selecttext += " veclaa ON vedeaa.cod_cliente = veclaa.cod_codigo"
        # selecttext += " JOIN"
        # selecttext += " veveaa ON veveaa.cod_codigo = veclaa.cod_vendedor"
        # selecttext += " WHERE veveaa.dat_nombre='"+str(vendedor_param)+"'"
        # selecttext += " AND (vedeaa.cod_cliente>="+cliente_desde+" and vedeaa.cod_cliente<="+cliente_hasta+")"
        # selecttext += " AND veclaa.dat_vercam=1"
        # selecttext += " GROUP BY"
        # selecttext += " 1, 2, 3, 4"
        # selecttext += ") AS subquery"
        # selecttext += " WHERE"
        # selecttext += " subquery.Saldo <> 0"
        # selecttext += " ORDER BY"
        # selecttext += " subquery.Saldo"



    resultado=informix_query(selecttext)

    try:
        #filtrar saldos 0
        resultado=resultado[resultado['saldo']!=0]
        print(resultado)
        codigo=resultado['codigo'].values.tolist()
        razon_social=resultado['razonsocial'].values.tolist()
        saldo=resultado['saldo'].values.tolist()

    except:
        codigo=[]
        razon_social=[]
        saldo=[]

    #demo!
    #labels=["Enero","Febrero","Marzo","Abril","Mayo"]
    #data=[210,313,321,124,512]
    #print(codigo)
    #print(razon_social)
    #print(saldo)

    data={
        'codigo': codigo,
        'razonsocial': razon_social,
        'saldo': saldo,
    }
    
   
      

    return JsonResponse(data)


def charts_rankingxcliente_home(request):

    return render(request, 'grafico_ranking_cliente.html')

def charts_listadosaldos_home(request):

    return render(request, 'grafico_listadosaldos.html')

def charts_vtaxdia_home(request):

    return render(request, 'grafico_vtaxdia.html')


def charts_vtaxvend_home(request):

    return render(request, 'grafico_vtaxvend.html')

def charts_vtaxmediopago_home(request):

    return render(request, 'grafico_vtaxmediopago.html')

def charts_vtaxperiodo_home(request):

    return render(request, 'grafico_vtaxperiodo.html')


def chart_dynamic_graph(request):

    FechaDesde="06/01/2023"
    FechaHasta="07/23/2023"
    Empresa="NANOLOG"
    

    desde = request.GET.get('from_date')  # Get the "desde" date from the query parameters
    hasta = request.GET.get('to_date')  # Get the "hasta" date from the query parameters


    FechaDesde=str(desde)
    FechaHasta=str(hasta)
    
    print(type(desde))
    print(desde)

    
    FechaDesde=convert_date_format(desde)
    FechaHasta=convert_date_format(hasta) 
    
    
    selecttext = "SELECT VETCAA.dat_tipo AS MEDIOPAGO, SUM(VETCAA.imp_total*VETCAA.dat_signo*VETCAA.imp_paripeso) AS Total FROM VETCAA"
    selecttext += " INNER JOIN GZEMAA on VETCAA.cod_ce_empresa=GZEMAA.cod_ce_empresa and gzemaa.dat_vercam=1"
    selecttext += " WHERE VETCAA.dat_tipo<>'ZZZ' and (VETCAA.fec_fechacompro>='"+ FechaDesde  +"' and VETCAA.fec_fechacompro<='"+FechaHasta+"')"
    selecttext += " and GZEMAA.dat_ce_razonsocial='"+Empresa+"'"
    selecttext += " GROUP BY VETCAA.DAT_TIPO"

    resultado=informix_query(selecttext)

    try:
        print(resultado)
        #VtaxVendedor=resultado['Vend'].values[0]
        labels=resultado['mediopago'].values.tolist()
        data=resultado['total'].values.tolist()

    except:
        print(resultado)
        labels=[]
        data=[]

    #labels=["Enero","Febrero","Marzo","Abril","Mayo"]
    #data=[210,313,321,124,512]
        
    print(labels)

    #reemplazar titulos
    #ej CA por CAJA
    for i in range(len(labels)):
        if labels[i]=="CA":
            labels[i]="Caja"

        if labels[i]=="TA":
            labels[i]="Tarjetas"

        if labels[i]=="OT":
            labels[i]="Otros"
   
    return JsonResponse({
        'labels': labels,
        'data': data,
    })