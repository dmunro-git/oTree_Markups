

library(readr)
treatments_Curtis <- read_csv("~/Dropbox/SSEL/otree_hotMarkukups/_misc/treatments_Curtis.csv")
treatmentParameterizations <- read_csv("~/Dropbox/SSEL/otree_hotMarkukups/_misc/treatmentParameterizations.csv")

n_sub_periods = 20

# create treatments in syntax otree can use. 

fileConn<-file("~/Dropbox/SSEL/otree_hotMarkukups/_misc/treatment_text.txt") #may need to rewrite this
fullText = ""
for (TreatmentNum in unique(treatments_Curtis$Treatment)){
  

  #SET UP FIRST HALF OF TREATMENTS
  df_treatment = treatments_Curtis %>% filter(Treatment == TreatmentNum)
  
  df_treatment_1st_half = left_join(df_treatment, treatmentParameterizations, by = c("ID_First_half_round"="ID"))
  df_treatment_2nd_half = left_join(df_treatment, treatmentParameterizations, by = c("ID_Second_half_round"="ID"))

  #s and t are shopping cost/ transport cost. 
  t = "
  't':[      #shopping cost, each element is one subperiod in a period. 
"
  mc = "
  'mc':[     #firm mill cost, or per item cost, each element is one subperiod in a period. 
"
  rp = "
  'rp':[     # consumer reserve price,  each element is one subperiod in a period. 
"
  for (period in df_treatment$Round){
    
    t = paste(
      t,
      paste(
        "    [",
        paste(
          rep(
            format((df_treatment_1st_half %>% filter(Round == period))$s,nsmall = 2),
            n_sub_periods/2
          ),
          collapse = ", "
        ),
        ",",
        paste(
          rep(
            format((df_treatment_2nd_half %>% filter(Round == period))$s,nsmall = 2),
            n_sub_periods/2
          ),
          collapse = ", "
        ),
  "],
"
      )
    )
    
    
    mc = paste(
      mc,
      paste(
        "    [",
        paste(
          rep(
            format((df_treatment_1st_half %>% filter(Round == period))$c,nsmall = 2),
            n_sub_periods/2
          ),
          collapse = ", "
        ),
        ",",
        paste(
          rep(
            format((df_treatment_2nd_half %>% filter(Round == period))$c,nsmall = 2),
            n_sub_periods/2
          ),
          collapse = ", "
        ),
  "],
"
      )
      )

    rp = paste(
      rp,
      paste(
        "    [",
        paste(
          rep(
            format((df_treatment_1st_half %>% filter(Round == period))$v,nsmall = 2),
            n_sub_periods/2
          ),
          collapse = ", "
        ),
        ",",
        paste(
          rep(
            format((df_treatment_2nd_half %>% filter(Round == period))$v,nsmall = 2),
            n_sub_periods/2
          ),
          collapse = ", "
        ),
  "],
"
      )
      )
    
    
  }
  t = paste(t, "  ],  #shopping cost, each element is one subperiod in a period. 

")
  mc = paste(mc, "  ],  #firm mill cost, or per item cost, each element is one subperiod in a period.  

            ")
  rp = paste(rp, "  ],  # consumer reserve price,  each element is one subperiod in a period.  

")
  
  
  df_treatment = treatments_Curtis %>% filter(Treatment == TreatmentNum)
  num_players = unique(df_treatment$Players)
  TreatmentName = unique(df_treatment$TreatmentDescription)
  
  
  
  
result = ""  
result = paste(
result,
"{

  'display_name': ","'Hotelling Mark-Up: ",num_players,"-Player, ",TreatmentName,"',

  'name': ","'HotMarkUps_",num_players,"Player_",gsub(" ", "_", TreatmentName),"',",
"
  'app_sequence': [
    'hotellingmarketup_00',
",

ifelse(num_players == '2', "    'hotellingmarkup_2p',","    'hotellingmarkup',"),

"
  ],
  'num_demo_participants': ",num_players,", # number of participants per group set in  models

  'loc':None, # set with array [ ], if None, then spaced (1/N)/2 apart
  
  #Number of Periods defined by number of arrays in t, mc and rp below. 
  
  'numSubperiods' :20, # number of subperiods in a period. 
  # if large, ensure 'num_rounds' in the app hotellingmarkup models.py is sufficently large
  'subperiod_time': 10, # length, in seconds, of a subperiod
  
  # below, each array indicate subperiod values for t, mc, and rp (and whatever else)
  # if there are too few elements in a period's array, the array is repeated until numSubperiods. 
  
",
t,
"",
mc,
"",
rp,
"",
sep = ""
)


result = paste(
  result,
  "},",
  sep = ""
) 
  
print(TreatmentNum)
fullText = paste(fullText, result)
  # rm(result)
  
}
writeLines(fullText, fileConn)  

close(fileConn)
