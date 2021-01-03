Data <- read.csv("/Users/vivien/Semester Munchen/Mapping Project/Git/searching-for-the-essentials/input-data/who/WHO-COVID-19-global-data.csv", header = TRUE, sep = "\t")

Data$Country_code <- Data$WHO_region <- Data$Cumulative_cases  <- Data$Cumulative_deaths <- Data$New_deaths <- NULL

Data <- Data[Data$Country == "Germany" | Data$Country == "Netherlands" | Data$Country == "The United Kingdom", ]

path <- "/Users/vivien/Semester Munchen/Mapping Project/Git/searching-for-the-essentials/output-data"
write.csv(Data, file.path(path, "data_who_clean.csv"), row.names=TRUE)


