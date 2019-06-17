import quandl

quandl.api_config.save_key("CfoUtV9wqsC4pedb9839")
data = quandl.get("EIA/PET_RWTC_D")
print(data)