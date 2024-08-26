from flask import Flask, jsonify, request
import json
import pandas as pd

app = Flask(__name__)

'''
@app.route("/")
def root():
    return "Home"
'''
def formar_response(p_gasfiredbig1, p_gasfiredbig2, p_gasfiredsomewhatsmaller, p_tj1, p_windpark1, p_windpark2):

    response =[
    {
        "name": "windpark1",
        "p": p_windpark1
    },
    {
        "name": "windpark2",
        "p": p_windpark2
    },
    {
        "name": "gasfiredbig1",
        "p": p_gasfiredbig1
    },
    {
        "name": "gasfiredbig2",
        "p": p_gasfiredbig2
    },
    {
        "name": "gasfiredsomewhatsmaller",
        "p": p_gasfiredsomewhatsmaller
    },
    {
        "name": "tj1",
        "p": p_tj1
    }
    ]
    return jsonify(response), 201 

@app.route("/power", methods=["POST"])
def calculate_power():
    
    ## Input
    if request.is_json:
        data = request.get_json()


        load=float(data['load'])
        gas=float(data['fuels']['gas(euro/MWh)'])
        kerosine=float(data['fuels']['kerosine(euro/MWh)'])
        co2=float(data['fuels']['co2(euro/ton)'])
        wind=float(data['fuels']['wind(%)'])
        powerplants = list(data['powerplants'])

        
        ### Creo un dataframe a partir de la lista de diccionarios
        df = pd.DataFrame.from_records(powerplants)

        ### Agrego al datafreame creado en el paso anterior los campos generales
        df['load'] = load 
        df['gas'] = gas
        df['kerosine'] = kerosine
        df['co2'] = co2
        df['wind'] = wind

        '''
        Columnas calculadas
            Coste:
                Necesitamos calcular 'unidades de electricidad' para llegar al Load.

                Por tanto necesitamos calcular em primero lugar el coste para generar una unidad de electrididad por cada planta
                para tenerlo en cuenta a la hora de priorizar plantas segun su coste de producción.
                
                - Gas: Cuesta 13.4 euros con una eficiencia del 53%, por tanto generar una unidad de electridad 
                costara casi el doble: (1 X 13.4)/0.53 = 25.28 €
                
                - Kerosine: misma formula que gas

                - Wind: Se comenta que no tiene coste por tanto 0
        '''
        ### Coste Unitario
        df.loc[df['type'] == 'gasfired', 'coste unit.'] = df['gas']/df['efficiency'] 
        df.loc[df['type'] == 'turbojet', 'coste unit.'] = df['kerosine']/df['efficiency'] 
        df.loc[df['type'] == 'windturbine', 'coste unit.'] = 0

        ### Power generado por Wind
        df.loc[df['type'] == 'windturbine', 'power wind.'] = df['pmax']*(df['wind']/100) 


        ### Nuevo Load. Se resta el Power Wind al load total
        df['Sum power wind.'] = df['power wind.'].sum()
        df['Load (new)'] = df['load'] - df['Sum power wind.']

        ### Almacenamos el power de las dos plantas de Wind:
        df_windpark1 = df[df['name'] == 'windpark1']
        p_windpark1 = float(df_windpark1['power wind.'])

        df_windpark2 = df[df['name'] == 'windpark2']
        p_windpark2 = float(df_windpark2['power wind.'])

        
        ### Nuevo dataframe sin Wind
        not_zero = df['type'] != 'windturbine'
        df2 = df[not_zero].sort_values('coste unit.',ascending=True)

        ### Iteración por filas del DataFrame:
        rest = float(df['Load (new)'].head(1))
        d = {}

        for index, row in df2.iterrows():
            if row['pmax'] <= rest:
                rest = rest - row['pmax']
                d['p_'+ row['name']] = row['pmax']

            else:
                d['p_'+ row['name']] = rest
                break

        #Rellenamos las variables finales
        if 'p_gasfiredbig1' in d:
            p_gasfiredbig1 = d['p_gasfiredbig1']
        if 'p_gasfiredbig2' in d:
            p_gasfiredbig2 = d['p_gasfiredbig2']
        if 'p_gasfiredsomewhatsmaller' in d:
            p_gasfiredsomewhatsmaller2 = d['p_gasfiredsomewhatsmaller']
        if 'p_tj1' in d:
            p_tj1 = d['p_tj1']
        
        if 'p_tj1' not in d:
            p_tj1 = 0
        if 'p_gasfiredbig1' not in d:
            p_gasfiredbig1 = 0
        if 'p_gasfiredbig2' not in d:
            p_gasfiredbig2 = 0
        if 'p_gasfiredsomewhatsmaller' not in d:
            p_gasfiredsomewhatsmaller = 0
 
        return formar_response(p_gasfiredbig1, p_gasfiredbig2, p_gasfiredsomewhatsmaller, p_tj1, p_windpark1, p_windpark2)
    else:
        return "Especificar entrada"
    

if __name__ == "__main__":
    app.run(debug=True, port=8888)

    '''
    def formar_response(p_gasfiredbig1, p_gasfiredbig2, p_gasfiredsomewhatsmaller, p_tj1, p_windpark1, p_windpark2):
    
        ## Variables resultado
        p1 = 90.0
        p2 = 21.6
        p3 = 460.0
        p4 = 338.4
        p5 = 0.0
        p6 = 0.0

        response =[
        {
            "name": "windpark1",
            "p": p_windpark1
        },
        {
            "name": "windpark2",
            "p": p_windpark2
        },
        {
            "name": "gasfiredbig1",
            "p": p_gasfiredbig1
        },
        {
            "name": "gasfiredbig2",
            "p": p_gasfiredbig2
        },
        {
            "name": "gasfiredsomewhatsmaller",
            "p": p_gasfiredsomewhatsmaller
        },
        {
            "name": "tj1",
            "p": p_tj1
        }
        ]
        #return jsonify(response), 201  
        print(response)

    f = open("payload.json")
    data = json.load(f)
    
    load=float(data['load'])
    gas=float(data['fuels']['gas(euro/MWh)'])
    kerosine=float(data['fuels']['kerosine(euro/MWh)'])
    co2=float(data['fuels']['co2(euro/ton)'])
    wind=float(data['fuels']['wind(%)'])
    powerplants = list(data['powerplants'])

    
    #print(powerplants)
    #Creo un dataframe a partir de la lista de diccionarios
    df = pd.DataFrame.from_records(powerplants)
    #Agrego al datafreame creado en el paso anterior los campos generales
    df['load'] = load 
    df['gas'] = gas
    df['kerosine'] = kerosine
    df['co2'] = co2
    df['wind'] = wind

    ''''''
    Columnas calculadas
        Coste:
            Necesitamos calcular 'unidades de electricidad' para llegar al Load.

            Por tanto necesitamos calcular em primero lugar el coste para generar una unidad de electrididad por cada planta
            para tenerlo en cuenta a la hora de priorizar plantas segun su coste de producción.
            
            - Gas: Cuesta 13.4 euros con una eficiencia del 53%, por tanto generar una unidad de electridad 
              costara casi el doble: (1 X 13.4)/0.53 = 25.28 €
            
            - Kerosine: misma formula que gas

            - Wind: Se comenta que no tiene coste por tanto 0
    ''''''
    #Coste Unitario
    df.loc[df['type'] == 'gasfired', 'coste unit.'] = df['gas']/df['efficiency'] 
    df.loc[df['type'] == 'turbojet', 'coste unit.'] = df['kerosine']/df['efficiency'] 
    df.loc[df['type'] == 'windturbine', 'coste unit.'] = 0

    #Power generado por Wind
    df.loc[df['type'] == 'windturbine', 'power wind.'] = df['pmax']*(df['wind']/100) 


    #Nuevo Load. Se resta el Power Wind al load total
    df['Sum power wind.'] = df['power wind.'].sum()
    df['Load (new)'] = df['load'] - df['Sum power wind.']

    #Almacenamos el power de Wind:
    df_windpark1 = df[df['name'] == 'windpark1']
    p_windpark1 = float(df_windpark1['power wind.'])
    #print(p_windpark1)

    df_windpark2 = df[df['name'] == 'windpark2']
    p_windpark2 = float(df_windpark2['power wind.'])
    #print(p_windpark2)

    print(p_windpark1+p_windpark2)
    
    #Nuevo dataframe sin Wind
    not_zero = df['type'] != 'windturbine'
    df2 = df[not_zero].sort_values('coste unit.',ascending=True)
    print(df2)

    # Iteración por filas del DataFrame:
 
    rest = float(df['Load (new)'].head(1))
    #print("Load (new): ", rest)
    d = {}

    for index, row in df2.iterrows():
        if row['pmax'] <= rest:
            rest = rest - row['pmax']
            #print('p_', row['name'], " :", row['pmax'])
            d['p_'+ row['name']] = row['pmax']

        else:
            #print('p_', row['name'], " :", rest)
            d['p_'+ row['name']] = rest
            break
    
    print(d)

    #print("p_gasfiredbig1= ", d["p_gasfiredbig1"])
    #print("p_gasfiredbig2= ", d["p_gasfiredbig2"])

    if 'p_gasfiredbig1' in d:
        p_gasfiredbig1 = d['p_gasfiredbig1']
    if 'p_gasfiredbig2' in d:
        p_gasfiredbig2 = d['p_gasfiredbig2']
    if 'p_gasfiredsomewhatsmaller' in d:
        p_gasfiredsomewhatsmaller2 = d['p_gasfiredsomewhatsmaller']
    if 'p_tj1' in d:
        p_tj1 = d['p_tj1']
    
    
    if 'p_tj1' not in d:
        p_tj1 = 0
    if 'p_gasfiredbig1' not in d:
        p_gasfiredbig1 = 0
    if 'p_gasfiredbig2' not in d:
        p_gasfiredbig2 = 0
    if 'p_gasfiredsomewhatsmaller' not in d:
        p_gasfiredsomewhatsmaller = 0

    
    formar_response(p_gasfiredbig1, p_gasfiredbig2, p_gasfiredsomewhatsmaller, p_tj1, p_windpark1, p_windpark2)
    '''