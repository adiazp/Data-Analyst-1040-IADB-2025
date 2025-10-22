import pandas as pd
import requests
import io
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import tenacity
from tenacity import retry

script_location = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_location) #Change current working directory to script location

@retry(stop=tenacity.stop_after_attempt(10))
def read_iadb(source,csize):
    """
    This function reads the Latin Macro Watch and SILAC files. 
    @retry is a decorator that will try running the function again if the data isn't downloaded.
    But, it will stop retrying after 10 attempts.
    
    Parameters
    ----------
    
    source : string
            The file to read, can only be "lmw" or "silac".
            
    Returns
    -------
    Pandas DataFrame
            CSV file with all the data imported as a Pandas DataFrame.
            I couldn't find documentation on how to use the API to grab specific indicators, countries and/or periods.
    """
    if source == "silac":
        dat = requests.get("https://data.iadb.org/datastore/dump/ba412771-9c90-4613-a96a-e18c005c0ab6?bom=True&format=csv")
        #return pd.read_csv(io.StringIO(dat.content.decode('utf-8')),dtype = {"country":"category"})
    else:
        dat = requests.get("https://data.iadb.org/datastore/dump/6c9d4ecc-4f05-4f63-9539-31f021f70c28?bom=True&format=csv")
    io_dat = io.BytesIO(dat.content)
    dat_reader = pd.read_csv(io_dat,chunksize = csize)
    dat_chunks = []
    for i in dat_reader:
        dat_chunks.append(i)
    dat = pd.concat(dat_chunks,ignore_index = True)
    return dat

#Read Latin Macro Watch data and change some variable values and formats

lmw = read_iadb(source="lmw",csize=100000)
print(lmw.columns)
lmw = lmw.rename(columns = {"Period":"year","Country":"country","Value":"value","Indicator":"indicator"})
lmw["indicator"] = lmw["indicator"].replace({"Primary Balance (Non Financial Public Sector)":"primary_balance","RER Multilateral":"RER"})
lmw["year"] = pd.to_datetime(lmw["Date"]).dt.year
lmw["country"] = lmw["country"].astype("category")

#Read SILAC data and change some variable values and formats

silac = read_iadb(source="silac",csize=100000)
print(silac.columns)
silac["year"] = pd.to_datetime(silac["dt"]).dt.year

#Grab iso codes to assign the isocode3 in this file to the country name using the LMW format

iso_codes_dl = requests.get("https://datahub.io/core/country-codes/_r/-/data/country-codes.csv")
iso_codes = pd.read_csv(io.StringIO(iso_codes_dl.content.decode('utf-8')))
iso_codes = iso_codes[["ISO3166-1-Alpha-3","official_name_en"]]
iso_codes["official_name_en"] = iso_codes["official_name_en"].replace({"Venezuela (Bolivarian Republic of)":"Venezuela","Bolivia (Plurinational State of)":"Bolivia"})
iso_codes = iso_codes.rename(columns = {"ISO3166-1-Alpha-3":"isoalpha3","official_name_en":"country"})

silac = silac.merge(iso_codes, on = ["isoalpha3"])
silac["country"] = silac["country"].astype("category")

#Only keep SILAC indicators that will be included in the analysis or will be transformed later

silac_target = ["jefa_ch",
"pdis_ch",
"anos_promedio_educ_sims",
"ninis_2_15_24",
"tasa_terminacion_c_secund",
"tasa_terminacion_c_terc",
"pobreza_lp2017",
"tasa_desocupacion",
"tenure_prom",
"dura_desempleo",
"horas_trabajadas",
"inglaboral_formales",
"inglaboral_informales",
"sal_menor_salmin",
"tasa_participacion",
"ptmc_ch",
"p90_10",
"dependency_ratio",
"tamh_ch",
"ingreso_mens_prom",
"salmin_mes",
"salminmes_ppp",
"ingreso_mens_prom_ppp2017"]

silac_filt = silac[silac["indicator"].isin(silac_target)]
print(silac_filt.info(verbose=True))

# Only keep totals for each of these demographic, geographic and miscellaneous variables
vars_cond = ["area","quintile","sex","education_level","age","ethnicity","language","disability","migration","management","funding"]

condstring  = ""
for i in vars_cond:
    condstring += i+" == 'Total' & "

condstring = condstring[:-3]

silac_filt2 = silac_filt.query(condstring)

#Only keep year, country, a variable showing the indicator in question and its value
silac_filt3 = silac_filt2[["year","country","indicator","value"]]

#Do the same for LMW, here I just considered 3 indicators
lmw_target = ['primary_balance',
              'CPI',
              'RER']
lmw_filt = lmw[lmw["indicator"].isin(lmw_target)]

#Only keep annual data
lmw_filt2 = lmw_filt[lmw_filt["Frequency"] == "Annual"]

#Create preliminary DataFrames for each indicator, then append into a single DataFrame
lmw_balance = lmw_filt2[(lmw_filt2["indicator"] == "primary_balance") & (lmw_filt2["Unit"] == "% of GDP")]
lmw_rer = lmw_filt2[(lmw_filt2["indicator"] == "RER") & (lmw_filt2["Unit"] == "index, period average")]
lmw_cpi = lmw_filt2[(lmw_filt2["indicator"] == "CPI") & (lmw_filt2["Unit"] == "period average inflation, %")]

lmw_filt3 = pd.concat([lmw_balance,lmw_cpi,lmw_rer],axis = 0)[["year","country","indicator","value"]]
lmw_filt3["value"] = lmw_filt3["value"].replace("n.a.",np.nan).astype(float) #Replace n.a. values for nans

#Now we append and sort the SILAC and LMW data into a single DataFrame
data = pd.concat([silac_filt3,lmw_filt3],axis=0,ignore_index = True)
data = data.sort_values(by=["indicator","country","year"],ascending = True)

#Change from long to wide format, turn the indexes into variables or column names
data2 = pd.pivot_table(data,columns = ["indicator"],index = ["country","year"], values = ["value"])
data3 = data2.reset_index(names=["country","year"])
columns1 = list(data3.columns.get_level_values(1))
columns1[0] = "country"
columns1[1] = "year"
data3.columns = columns1


#Divide inflation by 100 to make its format like the variables expressed as a percentage in SILAC data
data3["CPI"] = data3["CPI"]/100
data3["primary_balance"] = data3["primary_balance"]/100
    
#Transform some variables to get some predictors such as inflation on t-1 and some wage ratios
data3["CPI_1"] = data3.groupby(["country"])["CPI"].shift(1)
data3["salmin_total"] = data3["salmin_mes"]/data3["ingreso_mens_prom"]
data3["salfor_total"] = data3["inglaboral_formales"]/data3["ingreso_mens_prom"]
data3["salinfor_total"] = data3["inglaboral_informales"]/data3["ingreso_mens_prom"]

#Drop some wage levels that become redundant as ratios allow for better comparisons between countries with different income levels
data3 = data3.drop(columns = ["inglaboral_formales","inglaboral_informales","ingreso_mens_prom","salmin_mes"],axis = 1)

#Deal with missing data
data4 = data3.dropna(subset = ["ninis_2_15_24"]) #Drop missing values of the dependent variable
missingness = data4.isnull().mean() #Calculate the percentage of missingness for each variable
print(missingness)
drop_miss = missingness[missingness > .05].index #We will only keep variables with a missingness below 5%
data4 = data4.drop(columns = drop_miss, axis = 1)

#Now we will only keep countries and years with 10+ observations
country_counts = data4["country"].value_counts()
drop_countries = list(country_counts[country_counts < 10].index)
print(country_counts)
data4 = data4[~data4["country"].isin(drop_countries)]
year_counts = data4["year"].value_counts()
print(year_counts)

"""
We will also only keep data for Venezuela until 2014 because:
i) The hyperinflation distorts the distributions of some predictors like CPI, lagged CPI and the 90-10 ratio
ii) My understanding is that the quality of Venezuela's economic statistics is thought to have worsened as a result of the crisis
"""
vzl_index_drop = data4[(data4["country"] == "Venezuela") & (data4["year"] > 2014)].index
data4 = data4.drop(vzl_index_drop, axis = 0)
data4 = data4.rename(columns = {"CPI":"inflation","CPI_1":"inflation_minus_1"}) #So it is clear this is YoY inflation and not the price level

#Now check the correlation matrix for the design matrix to prevent severe cases of multicollinearity
data5 = pd.get_dummies(data4,columns = ["country","year"])
data6 = data5.dropna(axis=0)
X1 = data6.drop(columns = ["ninis_2_15_24"],axis = 1)
y = data6["ninis_2_15_24"]
corrmat1 = X1.corr()
tcorrmat1 = pd.DataFrame(np.tril(corrmat1,k=-1)).abs() # I generated this matrix to make analysis easier on my end
tcorrmat1.index = corrmat1.index
tcorrmat1.columns = corrmat1.columns
tcorrmat1["max"] = tcorrmat1.max(axis=1)

sns.heatmap(corrmat1, cmap='coolwarm')
plt.title("Correlation heatmap")
plt.savefig("corr_heatmap.jpeg",format="jpeg")
plt.show()
#Ultimately, all pairwise correlations were between -0.9 and 0.9 so we keep all the regressors 

#Export data, outputs for analysis and some summary statistics as CSV
data_final = data4
data_final.to_csv("data_final.csv",index=False)

summary_stats = data_final.describe()
summary_stats.to_csv("summary_stats.csv",index=True)

corrmat1.to_csv("corr_matrix.csv",index=True)
missingness.to_csv("missingness_variable.csv",index = True)
country_counts.to_csv("country_counts.csv",index = True)
year_counts.to_csv("year_counts.csv",index = True)