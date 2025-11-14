import sqlite3
import pandas as pd
import copernicusmarine
import xarray as xr
#from pathlib import Path
import time

def fds():
  d=time.time()
  con=sqlite3.connect('db') 
  df2=pd.read_sql_query('select * from ValsStatiquesM',con)
  df2.set_index(['longitude', 'latitude'], inplace=True)
  con.close()
  f=time.time()
  print('données statiques:', f-d)
  return df2

def fdd(min,max,valeur):
  d=time.time()
  """cred = Path.home() / ".copernicusmarine" / ".copernicusmarine-credentials"
  if not cred.exists():
      copernicusmarine.login('rramdane', 'Ab12345@')"""
  #va chercher les données et le retourne sous forme d'un dataset Xarray
  df=copernicusmarine.open_dataset(
    dataset_id="cmems_mod_glo_phy_my_0.083deg_P1M-m",
    variables=[valeur], #thetao : température , so : salinité
    minimum_longitude=min,    
    maximum_longitude=max,   
    minimum_latitude=-80,       
    maximum_latitude=80,        
    start_datetime="2001-09-01 00:00:00",          #le début de la mesure sous forme annee-mois-JourTheures:minutes:secondes
    end_datetime="2001-09-01 00:00:00",            #la fin de la mesure sous forme annee-mois-JourTheures:minutes:secondes
    minimum_depth=0.49402499198913574,    
    maximum_depth=0.49402499198913574,          
  )[valeur].isel(time=0, depth=0) #les vals dépendent de long, lat, depth et time, mais depth et time ne servent à rien ici donc on les enleve #,"thetao"]
  f=time.time()
  print('données dynamique :', f-d)
  return df

def prepa(dfs):
  lon=dfs.index.get_level_values("longitude").to_numpy() #on récupère les données statiques de dfs et on les attribut à lon et lat
  lat=dfs.index.get_level_values("latitude").to_numpy()
  dfs=dfs.reset_index()
  return lon,lat,dfs

def test(dfs,lon,lat,dfd,valeur):
  #on créer a qui va attribuer les valeurs aux lat et lon appropriés
  dfs[valeur]=dfd.sel(longitude=xr.DataArray(lon),latitude=xr.DataArray(lat),)
  return dfs

